import praw
import time
import string
import re
import requests
from datetime import datetime

vowels = r"[aeiouy]"
consonants = r"[b-df-hj-np-tv-xz]"
punctuation = r"[\"'’;:,.?!()-]"
end_punctuation = r"[.?!]"
connector_punctuation = r"[;:,]"
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
        num_syllables += max(1, len( # ensure each validated word is at least one syllable, as words like 'the' aren't matched
            re.findall(r"([aiouy]+" + vowels + "*)|" + # non-e vowels followed by any number of vowels
               r"([e]+" + consonants + ")(?=[a-z'-])|" + # 1 or more e followed by a consonant (including s and d) in the middle of a word
               r"([e]+[b-cf-hj-np-rtv-xz])(?=\s)|" + # 1 or more e followed by a consonant that is not s or d at the end of a word
               r"([e]" + vowels + "+)", # 1 e followed by one or more vowels syllable
               word.lower())))
    return num_syllables

def valid_syllables(line_1, line_2):
    syllables_1 = syllables(line_1)
    if not in_range(syllables_1): return False
    syllables_2 = syllables(line_2)
    if not in_range(syllables_2): return False
    return syllables_1 == syllables_2

# after some research, rhyming appears to be much harder than counting syllables
# it requires converting a word to its phonetics and stresses (which is hard to do)
# so, we are retrieving rhyming data from an external database instead
def does_rhyme(word_1, word_2):
    response = requests.get(apiBaseUrl + remove_punctuation(word_1))
    return any(obj["word"] == remove_punctuation(word_2) for obj in response.json());

def validate_line(line):
    for word in line:
        if (not re.search(vowels, word.lower()) or # no vowels in word
           len(word) != len(re.findall("|".join([vowels, consonants, punctuation]), word.lower())) or # there are unrecognized characters
           (word != str(line[-1]) and re.search(end_punctuation, word))): #end punc appears in not the last word
                return []
    return line

def run_couplet_bot(subreddit):
    for comment in subreddit.comments(limit = 100):
        linesOfComment = re.split("\n\n\n*", comment.body)
        wordsOfLine = [line.split() for line in linesOfComment] # .lower() not used here to preserve original string
        lines = list(map(validate_line, [word for word in wordsOfLine]))
        for line_1, line_2 in zip(lines, lines[1:]):
            if (not line_1 or not line_2) or (re.search(connector_punctuation, line_2[-1])):
                continue
            if valid_syllables(line_1, line_2) and does_rhyme(line_1[-1], line_2[-1]):
                with open("commented.txt", "a+") as comment_record:
                    comment_record.seek(0)
                    if comment.id not in comment_record.read():
                        try:
                            comment.reply(">*" + " ".join(line_1) + "*\n\n>*" + " ".join(line_2) + "*\n\n" + "Nice couplet! You're a poet! And I'm a bot.")
                            comment_record.seek(2)
                            comment_record.write(comment.id + "\n")
                        except Exception as e:
                            with open("exceptions.txt", "a+") as exceptions_log:
                                # a known exception is rate limit exceeded; the bot account has low reddit karma and has a very strict rate limit
                                exceptions_log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + str(e) + "\n")
                break

def main():
    reddit = authenticate()
    subreddit = reddit.subreddit(subredditName)
    while True:
        run_couplet_bot(subreddit)
        time.sleep(60)

main()
