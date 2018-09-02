# reddit-couplet-bot

A reddit bot that looks for couplets in comments. A couplet here is defined as two rhyming lines that have the same number of syllables.

First install the requirements with `pip install -r requirements.txt`. You can do this in `virtualenv`.

You will also need to create a Reddit application to access the Reddit API. It's recommended to add this application to a Reddit account created solely to be a bot (not your personal account). After that, fill in the missing information in `praw.ini.sample` with those credentials, rename the file to `praw.ini`, and run the bot with `py reddit-couplet-bot.py`.
