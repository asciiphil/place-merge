#!/usr/bin/env python

import sys
import time

import ttystatus

from source import *

# If similar placements are closer in time than this number of seconds, consider
# them to be duplicates.  /r/place always gave at least a 5 minute cooldown,
# so we'll use that as our window.
DUPLICATE_WINDOW = 300


if len(sys.argv) > 1:
    debug = True
    x = int(sys.argv[1])
    y = int(sys.argv[2])
else:
    debug = False
    x = 0
    y = 0
    
sources = [SourceF(), SourceELFAHBET(), SourceLepon(), SourceWgoodall()]
if not debug:
    dest_conn = sqlite3.connect('merged.sqlite')
    dest_cur = dest_conn.cursor()
    dest_cur.execute('DROP TABLE IF EXISTS placements')
    dest_cur.execute("""
CREATE TABLE placements (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author INTEGER
)""")
    dest_cur.execute('CREATE INDEX placements_timestamp_idx ON placements(timestamp)')
    dest_cur.execute('CREATE INDEX placements_color_idx ON placements(color)')
    dest_cur.execute('CREATE INDEX placements_author_idx ON placements(author)')
    dest_cur.execute('CREATE INDEX placements_position_idx ON placements(x, y)')

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() %PercentDone(done,total) (%Integer(x),%Integer(y)) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
    st['x'] = x
    st['y'] = y
    st['done'] = 0
    st['total'] = 1001 * 1001
    st.flush()

for s in sources:
    if debug:
        s.set_pixel(x, y)
    else:
        s.all_by_pixel()
    s.next()
    s.all_bitmaps()
    s.next_bitmap()

active_sources = [s for s in sources if not s.is_done]
bitmap_sources = [s for s in sources is not s.bitmap_done]
while len(active_sources) > 0 or len(bitmap_sources) > 0:
    pixel_sources = [s for s in active_sources if s.x == x and s.y == y]
    while len(pixel_sources) > 0:
        ref = sorted(pixel_sources, key=lambda s: s.timestamp)[0]
        timestamp = ref.timestamp
        color = ref.color
        author = ref.author
        change_sources = []
        # For each source, if the current placement matches our reference,
        # advance to the next one, because we've now handled this one.
        for s in pixel_sources:
            if s.color == color and \
               s.author[:10] == author[:10] and \
               s.timestamp - timestamp <= DUPLICATE_WINDOW:
                change_sources.append(s.name)
                if len(s.author) > author:
                    author = s.author
                s.next()
        if debug:
            print '{}  {:3} {:3} {:3}  {:16} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)), x, y, color, author, change_sources)
        else:
            dest_cur.execute('INSERT INTO placements VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, author))
        pixel_sources = [s for s in pixel_sources if not s.is_done and s.x == x and s.y == y]
    y += 1
    if y > 1000:
        x += 1
        y = 0
    active_sources = [s for s in active_sources if not s.is_done]
    if not debug:
        st['x'] = x
        st['y'] = y
        st['done'] += 1
        st.flush()
if not debug:
    dest_conn.commit()
    st.finish()
