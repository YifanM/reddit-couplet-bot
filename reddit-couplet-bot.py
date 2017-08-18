import praw
import time
import string

vowels = set("aeiou")
consonants = set(char for char in string.ascii_lowercase if char not in vowels)
min_syllables = 8
max_syllables = 12

def authenticate():
    reddit = praw.Reddit("reddit-couplet-bot")
    return reddit

def in_range(num):
    return num >= min_syllables and num <= max_syllables

def syllables(line):
    return 10

def valid_syllables(line_1, line_2):
    syllables_1 = syllables(line_1)
    if not in_range(syllables_1): return false
    syllables_2 = syllables(line_2)
    if not in_range(syllables_2): return false
    return syllables_1 == syllables_2

def does_rhyme(line_1, line_2):
    return True;

def run_couplet_bot(subreddit):
    for comment in subreddit.comments(limit = 100):
        lines = comment.body.splitlines()
        for line_1, line_2 in zip(lines, lines[1:]):
            if does_rhyme(line_1, line_2) and valid_syllables(line_1, line_2):
                print ("wow")
    time.sleep(60)

def main():
    reddit = authenticate()
    subreddit = reddit.subreddit("test")
    while True:
        run_couplet_bot(subreddit)

main()
