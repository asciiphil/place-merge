#!/usr/bin/env python

"""Creates a bitmap_placements table containing placements solely from imported
boards (ignoring imported placements).  Guaranteed time fidelity, but most
datasets have relatively sparse board dumps."""

import argparse
import glob
import os.path
import sqlite3

import ttystatus
import numpy as np

from common import *

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
args = parser.parse_args()

def add_bitmap(canvas, bitmap, timestamp, source, dest_cur):
    for y, x in np.array(np.where(canvas != bitmap)).T:
        dest_cur.execute('INSERT INTO bitmap_placements (timestamp, x, y, color, source) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, int(bitmap[y, x]), source))

dest_conn = sqlite3.connect(args.working_database)
dest_cur = dest_conn.cursor()
dest_cur.execute('DROP TABLE IF EXISTS bitmap_placements')
dest_cur.execute("""
CREATE TABLE bitmap_placements (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  source TEXT
)""")
dest_conn.commit()

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
dest_cur.execute('SELECT COUNT(*) FROM raw_boards')
st['total'] = dest_cur.fetchone()[0]

canvas = np.zeros((1000, 1000), np.uint8)
for row in dest_conn.execute('SELECT board, source FROM raw_boards ORDER BY timestamp'):
    board, source = row
    timestamp = board_timestamp(board)
    bitmap = board_bitmap(board)
    add_bitmap(canvas, bitmap, timestamp, source, dest_cur)
    dest_conn.commit()
    canvas = bitmap
    st['done'] += 1
    
dest_conn.commit()
