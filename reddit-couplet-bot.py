import praw
import time
import string
import re

#use regex instead for these strings?

vowels = set("aeiou")
consonants = set(char for char in string.ascii_lowercase if char not in vowels)
punctuation = set("\"'’;:,.?!()")
end_punctuation = set(".?!")
connector_punctuation = set(";:,")
min_syllables = 8
max_syllables = 12

def authenticate():
    reddit = praw.Reddit("reddit-couplet-bot")
    return reddit

def in_range(num):
    return num >= min_syllables and num <= max_syllables

def syllables(line):
    return 10 #todo

def valid_syllables(line_1, line_2):
    syllables_1 = syllables(line_1)
    if not in_range(syllables_1): return False
    syllables_2 = syllables(line_2)
    if not in_range(syllables_2): return False
    return syllables_1 == syllables_2

def does_rhyme(word_1, word_2):
    return True #todo

def validate_line(line):
    #print (line)
    if not line: return False
    for word in line: #combine these 3 cases together somehow
        if all(char.lower() not in vowels and char.lower() not in consonants for char in word):
            #print(1)
            return []
        elif any(char.lower() not in vowels and char.lower() not in consonants and char not in punctuation for char in word):
            #print(2)
            return []
        elif word != str(line[-1]) and any(char in end_punctuation for char in word):
            #print(3)
            return []
    return line

def run_couplet_bot(subreddit):
    for comment in subreddit.comments(limit = 100):
        lines = list(map(validate_line, [line.split() for line in re.split("\n\n\n*", comment.body)]))
        for line_1, line_2 in zip(lines, lines[1:]):
            if not line_1 or not line_2: continue
            elif any(char in connector_punctuation for char in line_2[-1]): continue
            if valid_syllables(line_1, line_2) and does_rhyme(line_1[-1], line_2[-1]):
                print ("@", line_1, line_2) #todo
    time.sleep(60)

def main():
    reddit = authenticate()
    subreddit = reddit.subreddit("yifantest")
    while True:
        run_couplet_bot(subreddit)

main()
