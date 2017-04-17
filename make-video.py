#!/usr/bin/env python

import argparse
import subprocess
import sqlite3

import numpy as np
import ttystatus

from common import *

FPS = 60  # video frames per second
SPF = 60  # /r/place seconds per frame

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--working-database', default='working.sqlite', help='Intermediate SQLite database to use.  Default: %(default)s.')
args = parser.parse_args()
db = sqlite3.connect(args.working_database)
db.row_factory = sqlite3.Row


def init_source(sources, source_name, current_timestamp):
    ffmpeg_command = [
        'ffmpeg',
        '-loglevel', 'error',
        '-nostats',
        '-nostdin',
        '-f', 'rawvideo',
        '-s', '1000x1000',
        '-pix_fmt', 'rgb24',
        '-r', str(FPS),
        '-i', '-',
        '-an',
        '-y',
        'video-{}.mp4'.format(source_name)
    ]
    ffmpeg = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
    canvas = np.zeros((1000, 1000), np.uint8)
    sources[source_name] = (current_timestamp, canvas, ffmpeg)
    
def output_frames(sources, current_timestamp):
    for source_name, (next_frame_timestamp, canvas, ffmpeg) in sources.iteritems():
        while next_frame_timestamp < current_timestamp:
            ffmpeg.stdin.write(STD_COLORS[canvas].tobytes())
            next_frame_timestamp += SPF
        sources[source_name] = (next_frame_timestamp, canvas, ffmpeg)


st = ttystatus.TerminalStatus(period=0.1)
st.format('%ElapsedTime() %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
st['done'] = 0
placement_count = db.execute('SELECT COUNT(*) FROM raw_placements').fetchone()[0]
board_count = db.execute('SELECT COUNT(*) FROM raw_boards').fetchone()[0]
st['total'] = placement_count + board_count

# each source[<name>] is a tuple: (next_frame_timestamp, canvas, ffmpeg)
sources = {}
placement_cursor = db.execute('SELECT * FROM raw_placements ORDER BY timestamp, x, y, source')
board_cursor = db.execute('SELECT * FROM raw_boards ORDER BY timestamp, source')
placement_row = placement_cursor.fetchone()
board_row = board_cursor.fetchone()
while placement_row is not None or board_row is not None:
    # See what the current time is.
    if board_row is None or placement_row['timestamp'] < board_row['timestamp']:
        timestamp = placement_row['timestamp']
    else:
        timestamp = board_row['timestamp']
    # Output any frames, if needed.
    output_frames(sources, timestamp)
    # Apply the current data.
    if board_row is None or placement_row['timestamp'] < board_row['timestamp']:
        source_name = placement_row['source']
        if source_name not in sources:
            init_source(sources, source_name, timestamp)
        sources[source_name][1][placement_row['y'], placement_row['x']] = placement_row['color']
        placement_row = placement_cursor.fetchone()
    else:
        source_name = board_row['source']
        if source_name not in sources:
            init_source(sources, source_name, timestamp)
        ts, cv, ffm = sources[source_name]
        sources[source_name] = (ts, board_bitmap(board_row['board']), ffm)
        board_row = board_cursor.fetchone()
    st['done'] += 1

for source_name, (next_frame_timestamp, canvas, ffmpeg) in sources.iteritems():
    ffmpeg.stdin.write(STD_COLORS[canvas].tobytes())
    ffmpeg.stdin.close()

st.finish()
