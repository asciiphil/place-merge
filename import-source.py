#!/usr/bin/env python

import argparse
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
    
class ImportPlaceScraper:
    def __init__(self, input_file, db_conn, source_name):
        self.input_file = input_file
        self.dest_db = db_conn
        self.source_db = sqlite3.connect(input_file.name)
        self.source_db.row_factory = sqlite3.Row
        self.source_name = source_name

    def run(self):
        # Set up cursors
        placement_cursor = self.source_db.cursor()
        bitmap_cursor = self.source_db.cursor()

        # Set up progress bar
        st = ttystatus.TerminalStatus(period=0.1)
        st.format('%ElapsedTime() %String(stage) %PercentDone(done,total) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
        st['stage'] = 'initializing'
        st['done'] = 0
        st.flush()

        # Figure out how much work there is to do.
        placement_cursor.execute('SELECT COUNT(*) FROM placements')
        bitmap_cursor.execute('SELECT COUNT(*) FROM starting_bitmaps')
        st['total'] = placement_cursor.fetchone()[0] + bitmap_cursor.fetchone()[0]

        st['stage'] = 'making room'
        st.flush()
        self.dest_db.execute('DELETE FROM raw_placements WHERE source = ?', (self.source_name,))
        self.dest_db.execute('DELETE FROM raw_boards WHERE source = ?', (self.source_name,))
        
        # Transfer placements
        st['stage'] = 'placements'
        st.flush()
        for row in self.source_db.execute('SELECT * FROM placements'):
            # NOTE: x and y are swapped in the source database!
            self.dest_db.execute('INSERT INTO raw_placements (timestamp, x, y, color, author, source) VALUES (?, ?, ?, ?, ?, ?)',
                                 (row['recieved_on'], row['y'], row['x'], row['color'], row['author'], self.source_name))
            st['done'] += 1

        # Transfer bitmaps
        st['stage'] = 'boards'
        st.flush()
        for row in self.source_db.execute('SELECT * FROM starting_bitmaps'):
            self.dest_db.execute('INSERT INTO raw_boards (timestamp, board, source) VALUES (?, ?, ?)',
                                 (board_timestamp(row['data']), row['data'], self.source_name))
            st['done'] += 1

        st['stage'] = 'finishing'
        st.flush()
        self.dest_db.commit()
        st.finish()

SCHEMAS = {
    'place-scraper': ImportPlaceScraper,
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
