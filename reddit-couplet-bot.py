import praw
import time
import string
import re
import requests
from datetime import datetime

vowels = r"[aeiouyAEIOUY]"
consonants = r"[b-df-hj-np-tv-xzB-DF-HJ-NP-TV-XZ]"
punctuation = r"[\"\'\’\;\:\,\.\?\!\(\)\-]"
end_punctuation = r"[\.\?\!]"
connector_punctuation = r"[\;\:\,]"
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
    num_syllables = len(re.findall(r"([aiouyAIOUY]+" + vowels + "*)|" + # non-e vowels followed by any number of vowels
                                   "([eE]+" + consonants + ")(?=[a-zA-Z'-])|" + # 1 or more e followed by a consonant (including s and d) in the middle of a word
                                   "([eE]+[b-cf-hj-np-rtv-xzB-CF-HJ-NP-RTV-XZ])\s|" + # 1 or more e followed by a consonant that is not s or d at the end of a word
                                   "([eE]" + vowels + "+)|" + # 1 e followed by one or more vowels 
                                   "(\s[tT][hH][eE]\s)", # special case for 'the'
                                       " ".join(line).lower()))
    num_syllables += max(1, num_syllables)
    return num_syllables

def valid_syllables(line_1, line_2):
    syllables_1 = syllables(line_1)
    if not in_range(syllables_1): return False
    syllables_2 = syllables(line_2)
    if not in_range(syllables_2): return False
    return syllables_1 == syllables_2

# after some research, rhyming appears to be much harder than counting syllables
# it requires converting a word to its phonetics and stresses (which seems to be very hard to do)
# so, we are retrieving rhyming data from an external database instead
def does_rhyme(word_1, word_2):
    response = requests.get(apiBaseUrl + remove_punctuation(word_1))
    return any(obj["word"] == remove_punctuation(word_2) for obj in response.json());

def validate_line(line):
    # if not line: return False <-- is it possible to receive an empty line?
    for word in line:
        if (not re.search(vowels, word.lower()) or # no vowels in word
           len(word) != len(re.findall("|".join([vowels, consonants, punctuation]), word.lower())) or # there are unrecognized characters
           (word != str(line[-1]) and re.search(end_punctuation, word))): #end punc appears in not the last word
                return []
    return line

def run_couplet_bot(subreddit):
    for comment in subreddit.comments(limit = 100):
        lines = list(map(validate_line, [line.split() for line in re.split("\n\n\n*", comment.body)]))
        for line_1, line_2 in zip(lines, lines[1:]):
            if (not line_1 or not line_2) or (re.search(connector_punctuation, line_2[-1])):
                #print(line_1, line_2)
                continue
            if valid_syllables(line_1, line_2) and does_rhyme(line_1[-1], line_2[-1]):
                #print(1)
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
