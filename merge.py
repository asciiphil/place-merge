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
    param_x = int(sys.argv[1])
    param_y = int(sys.argv[2])
else:
    debug = False

def write_pixel(timestamp, x, y, color, author, source, dest_cur, debug):
    if debug:
        print '{}  {:3} {:3} {:3}  {:16} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)), x, y, color, '' if author is None else author, source)
    else:
        dest_cur.execute('INSERT INTO placements VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, author))

def write_duplicate(timestamp, x, y, color, author, source, dest_cur, debug):
    if debug:
        print '           {}                              + {}'.format(time.strftime('%H:%M:%S', time.gmtime(timestamp)), source)
        
source_conn = sqlite3.connect('unpacked.sqlite')
source_cur = source_conn.cursor()
if debug:
    dest_cur = None
else:
    dest_conn = sqlite3.connect('merged.sqlite')
    dest_cur = dest_conn.cursor()
    dest_cur.execute('DROP TABLE IF EXISTS placements')
    dest_cur.execute("""
CREATE TABLE placements (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT
)""")
    dest_cur.execute('CREATE INDEX placements_timestamp_idx ON placements(timestamp)')
    dest_cur.execute('CREATE INDEX placements_color_idx ON placements(color)')
    dest_cur.execute('CREATE INDEX placements_author_idx ON placements(author)')
    dest_cur.execute('CREATE INDEX placements_position_idx ON placements(x, y)')

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() %PercentDone(done,total) (%Integer(x),%Integer(y)) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
    st['done'] = 0
    source_cur.execute('SELECT COUNT(*) FROM unpacked')
    st['total'] = source_cur.fetchone()[0]
    st.flush()

if debug:
    source_cur.execute('SELECT timestamp, x, y, color, author, source FROM unpacked WHERE x = ? AND y = ? ORDER BY timestamp', (param_x, param_y))
else:
    source_cur.execute('SELECT timestamp, x, y, color, author, source FROM unpacked ORDER BY x, y, timestamp')

last_x = None
last_y = None
for timestamp, x, y, color, author, source in source_cur:
    if not debug:
        st['x'] = x
        st['y'] = y
    if x != last_x or y != last_y:
        last_color = None
        last_source = None
        last_timestamp = 0
    # If there's no author, this is a synthetic event; only write it if it
    # changes the color of the pixel.
    # If there is an author, check for duplication.  It's a duplicate if it has
    # a different source than the last placement and is within the
    # DUPLICATE_WINDOW.
    if (author is None and color != last_color) or \
       (author is not None and (source == last_source or timestamp - last_timestamp >= DUPLICATE_WINDOW)):
        write_pixel(timestamp, x, y, color, author, source, dest_cur, debug)
        # Only update last_timestamp if this was a real placement, and then only
        # if it was written to the database.  This ensures that we only compare
        # to the earliest known time of the placement.
        if author is not None:
            last_timestamp = timestamp
    elif author is not None:
        # This is a real placement, so it must have been a duplicate
        write_duplicate(timestamp, x, y, color, author, source, dest_cur, debug)
    last_x = x
    last_y = y
    last_color = color
    last_source = source
    if not debug:
        st['done'] += 1
    
if not debug:
    dest_conn.commit()
    st.finish()
