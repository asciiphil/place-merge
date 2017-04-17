#!/usr/bin/env python

import argparse
import sqlite3

import numpy as np
import ttystatus
from PIL import Image

from common import *

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
args = parser.parse_args()
db = sqlite3.connect(args.working_database)
db.row_factory = sqlite3.Row

st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
placement_count = db.execute('SELECT COUNT(*) FROM raw_placements').fetchone()[0]
board_count = db.execute('SELECT COUNT(*) FROM raw_boards').fetchone()[0]
st['total'] = placement_count + board_count

canvases = {}
placement_cursor = db.execute('SELECT * FROM raw_placements ORDER BY timestamp, x, y, source')
board_cursor = db.execute('SELECT * FROM raw_boards ORDER BY timestamp, source')
placement_row = placement_cursor.fetchone()
board_row = board_cursor.fetchone()
while placement_row is not None or board_row is not None:
    if board_row is None or placement_row['timestamp'] < board_row['timestamp']:
        source_name = placement_row['source']
        if source_name not in canvases:
            canvases[source_name] = np.zeros((1000, 1000), np.uint8)
        canvases[source_name][placement_row['y'], placement_row['x']] = placement_row['color']
        placement_row = placement_cursor.fetchone()
    else:
        source_name = board_row['source']
        canvases[source_name] = board_bitmap(board_row['board'])
        board_row = board_cursor.fetchone()
    st['done'] += 1

for source_name, canvas in canvases.iteritems():
    Image.fromarray(STD_COLORS[canvas]).save('image-{}.png'.format(source_name))
