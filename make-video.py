#!/usr/bin/env python

import subprocess

import numpy as np
import ttystatus

from source import *

STD_COLORS = np.array([
    (255, 255, 255),
    (228, 228, 228),
    (136, 136, 136),
    (34, 34, 34),
    (255, 167, 209),
    (229, 0, 0),
    (229, 149, 0),
    (160, 106, 66),
    (229, 217, 0),
    (148, 224, 68),
    (2, 190, 1),
    (0, 211, 221),
    (0, 131, 199),
    (0, 0, 234),
    (207, 110, 228),
    (130, 0, 128),
], np.uint8)

FPS = 60  # video frames per second
SPF = 60  # /r/place seconds per frame

def output_frame(canvas, ffmpeg):
    ffmpeg.stdin.write(STD_COLORS[canvas].tobytes())

for source in [SourceELFAHBET(), SourceF(), SourceLepon(), SourceTea(), SourceWgoodall()]:
#for source in [SourceMerged()]:
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
        'Source{}.mp4'.format(source.name)
    ]
    ffmpeg = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

    canvas = np.zeros((1000, 1000), np.uint8)
    source.all_by_time()
    source.all_bitmaps()
    next_frame_ts = min(source.timestamp, source.bitmap_timestamp) - SPF

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() {} %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)'.format(source.name))
    st['done'] = 0
    st['total'] = source.count + source.bitmap_count

    while not source.is_done or not source.bitmap_done:
        if source.bitmap_done or source.timestamp < source.bitmap_timestamp:
            # Next data is from a pixel placement
            timestamp = source.timestamp
            while next_frame_ts < timestamp:
                output_frame(canvas, ffmpeg)
                next_frame_ts += SPF
            if source.x < 1000 and source.y < 1000:
                canvas[source.y, source.x] = source.color
            source.next()
        else:
            # Next data is from a bitmap
            timestamp = source.bitmap_timestamp
            while next_frame_ts < timestamp:
                output_frame(canvas, ffmpeg)
                next_frame_ts += SPF
            canvas = source.bitmap
            source.next_bitmap()
        st['done'] += 1

    ffmpeg.stdin.close()
    st.finish()

