#!/usr/bin/env python

import csv
import os
import sqlite3

import ttystatus

SOURCE_FILENAME = 'source-lepon01.csv'
DEST_FILENAME = 'source-lepon01.sqlite'

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
st['total'] = os.path.getsize(SOURCE_FILENAME)

with  sqlite3.connect(DEST_FILENAME) as dest_conn:
    dest_cur = dest_conn.cursor()
    dest_cur.execute("""
CREATE TABLE placements (
  id INTEGER NOT NULL PRIMARY KEY,
  recieved_on REAL,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT
)""")

    with open(SOURCE_FILENAME, 'r') as source_file:
        # NOTE: x and y appear to be swapped.
        source_csv = csv.DictReader(source_file, fieldnames=('id', 'x', 'y', 'user', 'color', 'timestamp'))
        for r in source_csv:
            dest_cur.execute('INSERT INTO placements (id, recieved_on, x, y, color, author) VALUES (?, ?, ?, ?, ?, ?)', (int(r['id']), float(r['timestamp']) / 1000, int(r['x']), int(r['y']), int(r['color']), r['user']))
            st['done'] = source_file.tell()
    dest_conn.commit()
st.finish()

