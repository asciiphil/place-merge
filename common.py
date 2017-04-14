#!/usr/bin/env python

import struct

import numpy as np

def board_timestamp(board):
    return struct.unpack('I', board[:4])[0]

def board_bitmap(board):
    arr = np.fromstring(board[4:500004], np.uint8)
    arr = arr.repeat(2)
    arr[::2] >>= 4
    arr[1::2] &= 0x0f
    return arr.reshape((1000, 1000))
