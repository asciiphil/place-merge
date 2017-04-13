#!/usr/bin/env python

import os.path

import ttystatus
import numpy as np

from source import *

sources = [SourceELFAHBET(), SourceF(), SourceLepon(), SourceTea(), SourceWgoodall()]
for source in sources:
    source.all_bitmaps()

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() %PercentDone(done,total) {} [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)'.format(source.name))
    st['done'] = 0
    st['total'] = source.bitmap_count
    
    while not source.bitmap_done:
        timestamp = source.bitmap_timestamp
        bitmap = source.bitmap
        np.save(os.path.join('bitmaps', '{}-{}.npy'.format(timestamp, source.name)), bitmap)
        source.next_bitmap()
        st['done'] += 1

    st.finish()
    
