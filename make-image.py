#!/usr/bin/env python

import numpy as np
import ttystatus
from PIL import Image

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

source = SourceLepon()
for source in [SourceELFAHBET(), SourceF(), SourceLepon(), SourceWgoodall()]:
#for source in [SourceMerged()]:
    canvas = np.zeros((1001, 1001), np.uint8)
    source.all_by_time()
    source.next()

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() {} %PercentDone(done,total) (%Integer(x),%Integer(y)) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)'.format(source.name))
    st['done'] = 0
    st['total'] = source.count

    while not source.is_done:
        st['x'] = source.x
        st['y'] = source.y
        canvas[source.y, source.x] = source.color
        source.next()
        st['done'] += 1

    Image.fromarray(STD_COLORS[canvas]).save('Source{}.png'.format(source.name))
    st.finish()
