#!/usr/bin/env python

import sqlite3

class Source(object):
    def __init__(self):
        self.connection = sqlite3.connect(self.source_file)
        self.cursor = self.connection.cursor()

    def set_pixel(self, x, y):
        self.cursor.execute(self.query, (x, y))

    def next(self):
        self.record = self.cursor.fetchone()

    @property
    def is_done(self):
        return self.record is None

    @property
    def id(self):
        return self.record[0]

    @property
    def timestamp(self):
        return self.record[1]

    @property
    def x(self):
        return self.record[2]

    @property
    def y(self):
        return self.record[3]

    @property
    def color(self):
        return self.record[4]

    @property
    def author(self):
        return str(self.record[5])

class SourceELFAHBET(Source):
    @property
    def name(self):
        return 'ELFAHBET_SOOP'

    @property
    def source_file(self):
        return 'source-ELFAHBET_SOOP.sqlite'

    @property
    def query(self):
        return '''SELECT NULL, recieved_on, x, y, color, author FROM placements WHERE x = ? AND y = ? ORDER BY recieved_on'''

class SourceF(Source):
    @property
    def name(self):
        return 'F'

    @property
    def source_file(self):
        return 'source-F.sqlite'

    @property
    def query(self):
        return '''SELECT NULL, recieved_on, x, y, color, author FROM placements WHERE x = ? AND y = ? ORDER BY recieved_on'''

class SourceLepon(Source):
    @property
    def name(self):
        return 'lepon01'

    @property
    def source_file(self):
        return 'source-lepon01.sqlite'

    @property
    def query(self):
        return '''SELECT id, CAST(ROUND(recieved_on) AS INT), x, y, color, author FROM placements WHERE x = ? AND y = ? ORDER BY recieved_on'''

class SourceWgoodall(Source):
    @property
    def name(self):
        return 'wgoodall01'

    @property
    def source_file(self):
        return 'source-wgoodall01.sqlite'

    @property
    def query(self):
        return '''SELECT id, CAST(strftime('%s', timestamp) AS INT), x, y, color, author FROM place WHERE x = ? AND y = ? ORDER BY timestamp'''
