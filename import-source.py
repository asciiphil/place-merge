#!/usr/bin/env python

import argparse
import csv
import os.path
import sqlite3
import struct

import ttystatus
import numpy as np


def board_timestamp(board):
    return struct.unpack('I', board[:4])[0]

def board_bitmap(board):
    arr = np.fromstring(board[4:500004], np.uint8)
    arr = arr.repeat(2)
    arr[::2] >>= 4
    arr[1::2] &= 0x0f
    return arr.reshape((1000, 1000))


class Import(object):
    def __init__(self, input_file, db_conn, source_name):
        self.input_file = input_file
        self.dest_db = db_conn
        self.source_name = source_name

    def run(self):
        # Set up progress bar
        st = ttystatus.TerminalStatus(period=0.1)
        st.format('%ElapsedTime() %String(stage) %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
        st['stage'] = 'initializing'
        st['done'] = 0
        st.flush()

        # Figure out how much work there is to do.
        st['total'] = self.total_items

        # Transfer placements
        st['stage'] = 'placements'
        st.flush()
        for timestamp, x, y, color, author in self.iter_placements():
            self.dest_db.execute('INSERT INTO raw_placements (timestamp, x, y, color, author, source) VALUES (?, ?, ?, ?, ?, ?)',
                                 (timestamp, x, y, color, author, self.source_name))
            st['done'] = self.get_placement_status(st['done'])

        # Transfer bitmaps
        st['stage'] = 'boards'
        st.flush()
        for board in self.iter_boards():
            self.dest_db.execute('INSERT INTO raw_boards (timestamp, board, source) VALUES (?, ?, ?)',
                                 (board_timestamp(board), board, self.source_name))
            st['done'] = self.get_board_status(st['done'])

        st['stage'] = 'finishing'
        st.flush()
        self.dest_db.commit()
        st.finish()
        
class ImportMoustacheMiner(Import):
    def __init__(self, input_file, db_conn, source_name):
        super(ImportMoustacheMiner, self).__init__(input_file, db_conn, source_name)
        self.source_csv = csv.DictReader(self.input_file, fieldnames=('id', 'x', 'y', 'user', 'color', 'timestamp'))

    @property
    def total_items(self):
        return os.path.getsize(self.input_file.name)

    def iter_placements(self):
        for row in self.source_csv:
            yield (float(row['timestamp']) / 1000, int(row['x']), int(row['y']), int(row['color']), row['user'])

    def get_placement_status(self, old_count):
        return self.input_file.tell()
        
    def iter_boards(self):
        return []

    def get_board_status(self, old_count):
        return old_count
        
class ImportPlaceScraper(Import):
    def __init__(self, input_file, db_conn, source_name):
        super(ImportPlaceScraper, self).__init__(input_file, db_conn, source_name)
        self.source_db = sqlite3.connect(self.input_file.name)
        self.source_db.row_factory = sqlite3.Row

    @property
    def total_items(self):
        placement_cursor = self.source_db.execute('SELECT COUNT(*) FROM placements')
        bitmap_cursor = self.source_db.execute('SELECT COUNT(*) FROM starting_bitmaps')
        return placement_cursor.fetchone()[0] + bitmap_cursor.fetchone()[0]

    def iter_placements(self):
        for row in self.source_db.execute('SELECT * FROM placements'):
            yield (row['recieved_on'], row['x'], row['y'], row['color'], row['author'])

    def get_placement_status(self, old_count):
        return old_count + 1
        
    def iter_boards(self):
        for row in self.source_db.execute('SELECT * FROM starting_bitmaps'):
            yield row['data']

    def get_board_status(self, old_count):
        return old_count + 1

class ImportPlaceScraperSwapped(ImportPlaceScraper):
    def iter_placements(self):
        for row in self.source_db.execute('SELECT * FROM placements'):
            # NOTE: x and y are swapped in the source database!
            yield (row['recieved_on'], row['y'], row['x'], row['color'], row['author'])

class ImportWgoodall01(Import):
    def __init__(self, input_file, db_conn, source_name):
        super(ImportWgoodall01, self).__init__(input_file, db_conn, source_name)
        self.source_db = sqlite3.connect(self.input_file.name)
        self.source_db.row_factory = sqlite3.Row

    @property
    def total_items(self):
        placement_cursor = self.source_db.execute('SELECT COUNT(*) FROM place WHERE timestamp IS NOT NULL')
        bitmap_cursor = self.source_db.execute('SELECT COUNT(*) FROM bitmap WHERE LENGTH(bitmap) >= 500000')
        return placement_cursor.fetchone()[0] + bitmap_cursor.fetchone()[0]

    def iter_placements(self):
        for row in self.source_db.execute('SELECT CAST(strftime(\'%s\', timestamp) AS INT) AS timestamp, x, y, color, author FROM place WHERE timestamp IS NOT NULL'):
            yield (row['timestamp'], row['x'], row['y'], row['color'], row['author'])

    def get_placement_status(self, old_count):
        return old_count + 1
        
    def iter_boards(self):
        for row in self.source_db.execute('SELECT bitmap FROM bitmap WHERE LENGTH(bitmap) >= 500000'):
            yield row['bitmap']

    def get_board_status(self, old_count):
        return old_count + 1

    
SCHEMAS = {
    'moustacheminer': ImportMoustacheMiner,
    'place-scraper': ImportPlaceScraper,
    'place-scraper-swapped': ImportPlaceScraperSwapped,
    'wgoodall01': ImportWgoodall01,
}

class ListSchemaAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ListSchemaAction, self).__init__(option_strings, dest, nargs=0, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        for schema_name in sorted(SCHEMAS.keys()):
            print schema_name
        exit(0)

parser = argparse.ArgumentParser()
parser.add_argument('--list-schemas', action=ListSchemaAction, help='List available schemas.')
parser.add_argument('-s', '--schema', required=True, choices=SCHEMAS.keys(),
                    help='Schema to use for the source.  Use --list-schemas to list known schemas.')
parser.add_argument('-n', '--name', help='Name to use for the dataset.  If unset, defaults to the schema used.')
parser.add_argument('-o', '--output', default='working.sqlite', help='Intermediate SQLite database to use.  Will be created if it doesn\'t exist.  Default: %(default)s.')
parser.add_argument('input', type=argparse.FileType('r'), help='File containing the source dataset.')
args = parser.parse_args()

if args.name is None:
    args.name = args.schema
    
dest_conn = sqlite3.connect(args.output)
dest_cur = dest_conn.cursor()
dest_cur.execute("""
CREATE TABLE IF NOT EXISTS raw_placements (
  timestamp REAL,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author TEXT,
  source TEXT
)""")
dest_cur.execute("""
CREATE TABLE IF NOT EXISTS raw_boards (
  timestamp REAL,
  board BLOB,
  source TEXT
)""")
dest_conn.commit()

importer = SCHEMAS[args.schema](args.input, dest_conn, args.name)
importer.run()
