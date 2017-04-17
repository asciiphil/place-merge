#!/usr/bin/env python

import argparse
import sqlite3

import ttystatus

from common import *

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
args = parser.parse_args()
db = sqlite3.connect(args.working_database)
db.row_factory = sqlite3.Row

db.execute("""
CREATE TABLE IF NOT EXISTS offsets (
  source TEXT,
  timestamp REAL,
  offset REAL,
  PRIMARY KEY(source, timestamp)
)""")

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
placement_count = db.execute('SELECT COUNT(*) FROM known_placements').fetchone()[0]
st['total'] = placement_count
st.flush()

for known_row in db.execute('SELECT * FROM known_placements'):
    for raw_row in db.execute('SELECT COUNT(*), source FROM raw_placements WHERE x = ? AND y = ? AND color = ? AND author = ? GROUP BY source',
                              (known_row['x'], known_row['y'], known_row['color'], known_row['author'])):
        if raw_row[0] == 1:
            row = db.execute('SELECT * FROM raw_placements WHERE x = ? AND y = ? AND color = ? AND author = ? GROUP BY source',
                             (known_row['x'], known_row['y'], known_row['color'], known_row['author'])).fetchone()
            db.execute('INSERT OR REPLACE INTO offsets (source, timestamp, offset) VALUES (?, ?, ?)', (row['source'], row['timestamp'], known_row['timestamp'] - row['timestamp']))
    st['done'] += 1
db.commit()
st.finish()
