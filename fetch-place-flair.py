#!/usr/bin/env python

import argparse
import codecs
import re
import sqlite3
import sys
import time

import praw

USER_AGENT = '/r/place flair scraper (by /u/phil_g)'
TOP_SUBMISSION_COUNT = 1000  # How many submissions to fetch.
# How many times per submission to fetch "More comments...".  Higher numbers
# will be more thorough, but will take much longer, since each one is a
# separate Reddit API call, and API users are limited to 60 calls per minute.
MORE_COMMENTS_COUNT = 60

# Assume stdout can always handle UTF-8/
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
args = parser.parse_args()
db = sqlite3.connect(args.working_database)

db.execute("""
CREATE TABLE IF NOT EXISTS known_placements (
  timestamp REAL,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT
)""")
db.commit()

def add_placement(timestamp, x, y, color, user, cursor):
    cursor.execute('SELECT COUNT(*) FROM known_placements WHERE timestamp = ? AND x = ? and y = ? and color = ? and author = ?', (timestamp, x, y, color, user))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO known_placements (timestamp, x, y, color, author) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, user))

cursor = db.cursor()
flair = {}
last_added = 0
reddit = praw.Reddit(user_agent=USER_AGENT)
subreddit = reddit.subreddit('place')
for submission in subreddit.top(limit=TOP_SUBMISSION_COUNT):
    print u'{}: {}...'.format(submission.id, submission.title)
    submission.comments.replace_more(limit=MORE_COMMENTS_COUNT)
    comment_queue = submission.comments[:]
    while comment_queue:
        comment = comment_queue.pop(0)
        if comment.author is not None and comment.author_flair_css_class is not None:
            if comment.author.name not in flair:
                color = int(comment.author_flair_css_class.split('-')[1])
                match = re.search('^\((\d+),(\d+)\) (\d+\.\d+)$', comment.author_flair_text)
                x = int(match.group(1))
                y = int(match.group(2))
                timestamp = float(match.group(3))
                flair[comment.author.name] = (timestamp, x, y, color)
                if x < 1000 and y < 1000:
                    print '{} ({},{}) {} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)), x, y, color, comment.author.name)
                    add_placement(timestamp, x, y, color, comment.author.name, cursor)
    print '...done ({} {}/{})'.format(submission.id, len(flair) - last_added, len(flair))
    last_added = len(flair)
    db.commit()


