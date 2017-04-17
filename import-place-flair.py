#!/usr/bin/env python

"""Goes through an HTML file from /r/place and pulls out people's last
pixel placements.  This gives known timestamps for particular
placements."""

import argparse
import re
import sys
import sqlite3

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
parser.add_argument('input', nargs='+', type=argparse.FileType('r'), help='HTML file with flair from /r/place.')
args = parser.parse_args()

known_conn = sqlite3.connect(args.working_database)
known_cur = known_conn.cursor()
known_cur.execute("""
CREATE TABLE IF NOT EXISTS known_placements (
  timestamp REAL,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT
)""")
known_conn.commit()

def add_placement(timestamp, x, y, color, user):
    known_cur.execute('SELECT COUNT(*) FROM known_placements WHERE timestamp = ? AND x = ? and y = ? and color = ? and author = ?', (timestamp, x, y, color, user))
    if known_cur.fetchone()[0] == 0:
        known_cur.execute('INSERT INTO known_placements (timestamp, x, y, color, author) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, user))

for input_file in args.input:
    print 'Reading {}...'.format(input_file.name)
    soup = BeautifulSoup(input_file.read(), 'lxml')
    for span in soup.find_all(attrs={'class':'flair'}):
        # class is "flair flair-place-n", where "n" is the color ID
        color = int(span['class'][1].split('-')[2])
        # title is "(x,y) timestamp"
        match = re.search('^\((\d+),(\d+)\) (\d+\.\d+)$', span['title'])
        x = int(match.group(1))
        y = int(match.group(2))
        timestamp = float(match.group(3))
        #
        user = span.previous_sibling.text
        add_placement(timestamp, x, y, color, user)
    known_conn.commit()
