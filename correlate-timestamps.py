#!/usr/bin/env python

import argparse
import sqlite3

import ttystatus

from common import *

# Largest offset we'll tolerate.  If we get a value bigger than this, we'll
# assume it's an error and ignore it.
MAX_DIFFERENCE = 1000

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
db.execute('DELETE FROM offsets')

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
placement_count = db.execute('SELECT COUNT(*) FROM known_placements').fetchone()[0]
st['total'] = placement_count
st.flush()

last_timestamps = {}
for known_row in db.execute('SELECT * FROM known_placements'):
    use_placement = True
    timestamps = {}
    for raw_row in db.execute('SELECT * FROM raw_placements WHERE x = ? AND y = ? AND color = ? AND author = ?',
                              (known_row['x'], known_row['y'], known_row['color'], known_row['author'])):
        source = raw_row['source']
        if source in timestamps:
            # Multiple entries for this placement.  Don't use it.
            use_placement = False
        elif source in last_timestamps and raw_row['timestamp'] < last_timestamps[source]:
            # Offset adjustment would put this placement earlier than the
            # previous placement.  We assume that this shouldn't happen (i.e.
            # placements are never logged out of order), so it means that
            # there are unlogged duplicates for this placement.  Don't use it.
            use_placement = False
        elif abs(known_row['timestamp'] - raw_row['timestamp']) > MAX_DIFFERENCE:
            use_placement = False
        else:
            # Looks good so far.
            timestamps[source] = raw_row['timestamp']
    if use_placement:
        for source, raw_timestamp in timestamps.iteritems():
            db.execute('INSERT OR REPLACE INTO offsets (source, timestamp, offset) VALUES (?, ?, ?)', (source, raw_timestamp, known_row['timestamp'] - raw_timestamp))
    last_timestamps = timestamps
    st['done'] += 1
db.commit()
st.finish()
