import praw
import time
import string
import re
import requests
from datetime import datetime

#use regex instead for these strings?

vowels = set("aeiouy")
consonants = set(char for char in string.ascii_lowercase if char not in vowels)
punctuation = set("\"'’;:,.?!()")
end_punctuation = set(".?!")
connector_punctuation = set(";:,")
min_syllables = 8
max_syllables = 12
apiBaseUrl = "https://api.datamuse.com/words?rel_rhy="
subredditName = "yifantest"

def authenticate():
    reddit = praw.Reddit("reddit-couplet-bot")
    return reddit

def in_range(num):
    return num >= min_syllables and num <= max_syllables

def remove_punctuation(word):
    return "".join([c for c in word if c not in punctuation])

#a heuristic to determine the number of syllables in a word
#1 syllable per vowel assuming it satisfies following conditions:
#don't count suffixes that end with -es -ed -e
#consecutive vowels only counts as one
def syllables(line):
    num_syllables = 0
    for word in line:
        temp = 0
        for index, char in enumerate(word):
            if char in vowels:
                if index != len(word) - 1 and word[index+1] in vowels:
                    continue
                elif index == len(word) - 1 and char == "e":
                    continue
                elif index == len(word) - 2 and (word.endswith("s") or word.endswith("d")):
                    continue
                temp += 1
        num_syllables += max(1, temp)
    return num_syllables

def valid_syllables(line_1, line_2):
    syllables_1 = syllables(line_1)
    if not in_range(syllables_1): return False
    syllables_2 = syllables(line_2)
    if not in_range(syllables_2): return False
    return syllables_1 == syllables_2

def does_rhyme(word_1, word_2):
    # after some research, rhyming appears to be much harder than counting syllables
    # it requires converting a word to its phonetics and stresses (which seems to be very hard to do)
    # so, we are retrieving rhyming data from an external database instead
    response = requests.get(apiBaseUrl + remove_punctuation(word_1))
    return any(obj["word"] == remove_punctuation(word_2) for obj in response.json());

def validate_line(line):
    # if not line: return False
    for word in line:
        if all(char.lower() not in vowels and char.lower() not in consonants for char in word) or
           any(char.lower() not in vowels and char.lower() not in consonants and char not in punctuation for char in word) or
           (word != str(line[-1]) and any(char in end_punctuation for char in word)):

            return []
    return line

def run_couplet_bot(subreddit):
    for comment in subreddit.comments(limit = 100):
        lines = list(map(validate_line, [line.split() for line in re.split("\n\n\n*", comment.body)]))
        for line_1, line_2 in zip(lines, lines[1:]):
            if (not line_1 or not line_2) or (any(char in connector_punctuation for char in line_2[-1])):
                continue
            if valid_syllables(line_1, line_2) and does_rhyme(line_1[-1], line_2[-1]):
                with open("commented.txt", "a+") as comment_record:
                    if comment.id not in comment_record.read(): # check that this still works
                        try:
                            comment.reply(">*" + " ".join(line_1) + "*\n\n>*" + " ".join(line_2) + "*\n\n" + "Nice couplet! You're a poet! And I'm a bot.")
                            comment_record.write(comment.id + "\n")
                        except Exception as e:
                            with open("exceptions.txt", "a+") as exceptions_log:
                                exceptions_log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + str(e) + "\n")
                break

def main():
    reddit = authenticate()
    subreddit = reddit.subreddit(subredditName)
    while True:
        run_couplet_bot(subreddit)
        time.sleep(60)

main()
