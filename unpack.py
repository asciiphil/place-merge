#!/usr/bin/env python

import ttystatus
import numpy as np

from source import *


def add_pixel(source, dest_cur):
    if source.x < 1000 and source.y < 1000:
        dest_cur.execute('INSERT INTO unpacked (timestamp, x, y, color, author, source) VALUES (?, ?, ?, ?, ?, ?)', (source.timestamp, source.x, source.y, source.color, source.author, source.name))

def canvas_update_pixel(canvas, source):
    if source.x < 1000 and source.y < 1000:
        canvas[source.y, source.x] = source.color
    
def add_bitmap(canvas, source, dest_cur):
    timestamp = source.bitmap_timestamp
    bitmap = source.bitmap
    for x, y in np.array(np.where(canvas != bitmap)).T:
        dest_cur.execute('INSERT INTO unpacked (timestamp, x, y, color, source) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, int(bitmap[y, x]), source.name))

def canvas_update_bitmap(canvas, source):
    np.copyto(canvas, source.bitmap)

dest_conn = sqlite3.connect('unpacked.sqlite')
dest_cur = dest_conn.cursor()
dest_cur.execute('DROP TABLE IF EXISTS unpacked')
dest_cur.execute("""
CREATE TABLE unpacked (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT,
  source TEXT
)""")
dest_cur.execute('CREATE INDEX pum_timestamp_idx ON unpacked(timestamp)')
dest_cur.execute('CREATE INDEX pum_position_idx ON unpacked(x, y)')

sources = [SourceELFAHBET(), SourceF(), SourceLepon(), SourceTea(), SourceWgoodall()]
for source in sources:
    source.all_by_time()
    source.all_bitmaps()
    
    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() %PercentDone(done,total) {} [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)'.format(source.name))
    st['done'] = 0
    st['total'] = source.count + source.bitmap_count
    
    canvas = np.zeros((1000, 1000), np.uint8)
    while not source.is_done or not source.bitmap_done:
        if not source.is_done and \
           (source.bitmap_done or source.timestamp <= source.bitmap_timestamp):
            add_pixel(source, dest_cur)
            canvas_update_pixel(canvas, source)
            source.next()
        else:
            add_bitmap(canvas, source, dest_cur)
            canvas_update_bitmap(canvas, source)
            source.next_bitmap()
        st['done'] += 1
    st.finish()
    
    dest_conn.commit()
