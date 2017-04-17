#!/usr/bin/env python

import argparse
import sqlite3
import sys
import time

import ttystatus

from common import *

# If similar placements are closer in time than this number of seconds, consider
# them to be duplicates.  /r/place always gave at least a 5 minute cooldown,
# so we'll use that as our window.
DUPLICATE_WINDOW = 300

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
parser.add_argument('-p', '--pixel', nargs=2, metavar=('X', 'Y'), type=int, help='Instead of merging data, print the merged timeline for the given pixel.')
args = parser.parse_args()
source_db = sqlite3.connect(args.working_database)
source_db.row_factory = sqlite3.Row

def new_pixel(canvas, row, dest_cur, st):
    x = row['x']
    y = row['y']
    # This pixel is a duplicate if:
    #  * It's the same color as the current pixel,
    #  * It's the same author as the current pixel, AND
    #  * It's within the window of duplication.
    if canvas[y, x]['color'] == row['color'] and \
       canvas[y, x]['author'] == row['author'] and \
       row['timestamp'] - canvas[y, x]['timestamp'] < DUPLICATE_WINDOW:
        duplicate_pixel(row['timestamp'], x, y, row['color'], row['author'], row['source'], dest_cur, st)
    else:
        update_pixel(row['timestamp'], x, y, row['color'], row['author'], row['source'], dest_cur, st)
    update_canvas(canvas, x, y, row['color'], row['timestamp'], row['author'])

def new_board(canvas, row, dest_cur, st):
    bitmap = board_bitmap(row['board'])
    if args.pixel is None:
        for y, x in np.array(np.where(canvas['color'] != bitmap)).T:
            update_pixel(row['timestamp'], x, y, bitmap[y, x], None, row['source'], dest_cur, st)
    else:
        x, y = args.pixel
        if canvas[y, x]['color'] != bitmap[y, x]:
            update_pixel(row['timestamp'], x, y, bitmap[y, x], None, row['source'], dest_cur, st)
    np.copyto(canvas, bitmap)
    
def update_pixel(timestamp, x, y, color, author, source, dest_cur, st):
    if args.pixel is None:
        if author is None:
            # Have to cast color to an int because sqlite3 doesn't understand numpy.uint8.
            dest_cur.execute('INSERT INTO placements (timestamp, x, y, color) VALUES (?, ?, ?, ?)', (timestamp, x, y, int(color)))
        else:
            dest_cur.execute('INSERT INTO placements (timestamp, x, y, color, author) VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, author))
    else:
        st.notify('{}  {:3} {:3} {:3}  {:16} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)), x, y, color, '' if author is None else author, source))

def duplicate_pixel(timestamp, x, y, color, author, source, dest_cur, st):
    if args.pixel is not None:
        st.notify('           {}                              + {}'.format(time.strftime('%H:%M:%S', time.gmtime(timestamp)), source))

def update_canvas(canvas, x, y, color, timestamp, author):
    canvas['color'][y, x]     = color
    canvas['timestamp'][y, x] = timestamp
    canvas['author'][y, x]    = author

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
board_count = source_db.execute('SELECT COUNT(*) FROM raw_boards').fetchone()[0]
if args.pixel is None:
    placement_count = source_db.execute('SELECT COUNT(*) FROM raw_placements').fetchone()[0]
else:
    placement_count = source_db.execute('SELECT COUNT(*) FROM raw_placements WHERE x = ? and y = ?', args.pixel).fetchone()[0]
st['total'] = placement_count + board_count
st.flush()

if args.pixel is None:
    dest_db = sqlite3.connect('merged.sqlite')
    dest_cur = dest_db.cursor()
    dest_cur.execute('DROP TABLE IF EXISTS placements')
    dest_cur.execute("""
CREATE TABLE placements (
  timestamp REAL,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT
)""")
    dest_cur.execute('CREATE INDEX placements_timestamp_idx ON placements(timestamp)')
    dest_cur.execute('CREATE INDEX placements_color_idx ON placements(color)')
    dest_cur.execute('CREATE INDEX placements_author_idx ON placements(author)')
    dest_cur.execute('CREATE INDEX placements_position_idx ON placements(x, y)')
else:
    dest_cur = None
    
if args.pixel is None:
    placement_cur = source_db.execute('SELECT * FROM raw_placements ORDER BY timestamp, x, y, source')
else:
    placement_cur = source_db.execute('SELECT * FROM raw_placements WHERE x = ? AND y = ? ORDER BY timestamp, source', args.pixel)
board_cur = source_db.execute('SELECT * FROM raw_boards ORDER BY timestamp, source')

canvas = np.empty((1000, 1000), dtype=[('color', 'u1'), ('timestamp', 'f4'), ('author', 'O')])
canvas['color'] = 0
canvas['timestamp'] = 1490979600
canvas['author'] = ''
placement_row = placement_cur.fetchone()
board_row = board_cur.fetchone()
while placement_row is not None or board_row is not None:
    if placement_row is not None and (board_row is None or placement_row['timestamp'] < board_row['timestamp']):
        new_pixel(canvas, placement_row, dest_cur, st)
        placement_row = placement_cur.fetchone()
    else:
        new_board(canvas, board_row, dest_cur, st)
        board_row = board_cur.fetchone()
    st['done'] += 1
if args.pixel is None:
    dest_db.commit()
