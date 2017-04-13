#!/usr/bin/env python

import glob
import os.path
import sqlite3

import ttystatus
import numpy as np

def add_bitmap(canvas, bitmap, timestamp, source, dest_cur):
    for x, y in np.array(np.where(canvas != bitmap)).T:
        dest_cur.execute('INSERT INTO placements (timestamp, x, y, color, source) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, int(bitmap[y, x]), source))

def canvas_update_bitmap(canvas, bitmap):
    np.copyto(canvas, bitmap)

dest_conn = sqlite3.connect('placements.sqlite')
dest_cur = dest_conn.cursor()
dest_cur.execute('DROP TABLE IF EXISTS placements')
dest_cur.execute("""
CREATE TABLE placements (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  source TEXT
)""")
dest_cur.execute('CREATE INDEX place_timestamp_idx ON placements(timestamp)')
dest_cur.execute('CREATE INDEX place_position_idx ON placements(x, y)')

filenames = glob.glob(os.path.join('bitmaps', '*'))

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
st['total'] = len(filenames)

canvas = np.zeros((1000, 1000), np.uint8)
for filename in filenames:
    base_filename = os.path.basename(filename)
    base_root, base_ext = os.path.splitext(base_filename)
    timestamp_str, source = base_root.split('-')
    timestamp = int(timestamp_str)

    bitmap = np.load(filename)
    add_bitmap(canvas, bitmap, timestamp, source, dest_cur)
    canvas_update_bitmap(canvas, bitmap)
    dest_conn.commit()
    st['done'] += 1
    
dest_conn.commit()
