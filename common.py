#!/usr/bin/env python

import struct

import numpy as np

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


def board_timestamp(board):
    return struct.unpack('I', board[:4])[0]

def board_bitmap(board):
    arr = np.fromstring(board[4:500004], np.uint8)
    arr = arr.repeat(2)
    arr[::2] >>= 4
    arr[1::2] &= 0x0f
    return arr.reshape((1000, 1000))
