#!/usr/bin/env python

import sqlite3

class Source(object):
    def __init__(self):
        self.connection = sqlite3.connect(self.source_file)
        self.cursor = self.connection.cursor()

    def set_pixel(self, x, y):
        self.cursor.execute(self.query_pixel_count, (x, y))
        self.count = self.cursor.fetchone()[0]
        self.cursor.execute(self.query_pixel, (x, y))

    def all_by_time(self):
        self.cursor.execute(self.query_all_count)
        self.count = self.cursor.fetchone()[0]
        self.cursor.execute(self.query_all_by_time)
        
    def all_by_pixel(self):
        self.cursor.execute(self.query_all_count)
        self.count = self.cursor.fetchone()[0]
        self.cursor.execute(self.query_all_by_pixel)
        
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
        """Unix epoch time (integer seconds since 1970-01-01T00:00:00 UTC)."""
        return self.record[1]

    @property
    def x(self):
        """Position along the horizontal axis."""
        return self.record[2]

    @property
    def y(self):
        """Position along the vertical axis."""
        return self.record[3]

    @property
    def color(self):
        """Integer, 0-15, inclusive."""
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
    def query_pixel(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements WHERE y = ? AND x = ? ORDER BY recieved_on'''

    @property
    def query_pixel_count(self):
        return '''SELECT COUNT(*) FROM placements WHERE y = ? AND x = ?'''

    @property
    def query_all(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements ORDER BY recieved_on, y, x'''

    @property
    def query_all_by_time(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements ORDER BY recieved_on, y, x'''

    @property
    def query_all_by_pixel(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements ORDER BY y, x, recieved_on'''

    @property
    def query_all_count(self):
        return '''SELECT COUNT(*) FROM placements'''

class SourceF(Source):
    @property
    def name(self):
        return 'F'

    @property
    def source_file(self):
        return 'source-F.sqlite'

    @property
    def query_pixel(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements WHERE y = ? AND x = ? ORDER BY recieved_on'''

    @property
    def query_pixel_count(self):
        return '''SELECT COUNT(*) FROM placements WHERE y = ? AND x = ?'''

    @property
    def query_all_by_time(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements ORDER BY recieved_on, y, x'''

    @property
    def query_all_by_pixel(self):
        return '''SELECT NULL, recieved_on, y, x, color, author FROM placements ORDER BY y, x, recieved_on'''

    @property
    def query_all_count(self):
        return '''SELECT COUNT(*) FROM placements'''

class SourceLepon(Source):
    @property
    def name(self):
        return 'lepon01'

    @property
    def source_file(self):
        return 'source-lepon01.sqlite'

    @property
    def query_pixel(self):
        return '''SELECT id, CAST(ROUND(recieved_on) AS INT), x, y, color, author FROM placements WHERE x = ? AND y = ? ORDER BY recieved_on'''

    @property
    def query_pixel_count(self):
        return '''SELECT COUNT(*) FROM placements WHERE x = ? AND y = ?'''

    @property
    def query_all_by_time(self):
        return '''SELECT id, CAST(ROUND(recieved_on) AS INT), x, y, color, author FROM placements ORDER BY recieved_on, x, y'''

    @property
    def query_all_by_pixel(self):
        return '''SELECT id, CAST(ROUND(recieved_on) AS INT), x, y, color, author FROM placements ORDER BY x, y, recieved_on'''

    @property
    def query_all_count(self):
        return '''SELECT COUNT(*) FROM placements'''

class SourceWgoodall(Source):
    @property
    def name(self):
        return 'wgoodall01'

    @property
    def source_file(self):
        return 'source-wgoodall01.sqlite'

    @property
    def query_pixel(self):
        return '''SELECT id, CAST(strftime('%s', timestamp) AS INT), x, y, color, author FROM place WHERE timestamp IS NOT NULL AND x = ? AND y = ? ORDER BY timestamp'''

    @property
    def query_pixel_count(self):
        return '''SELECT COUNT(*) FROM place WHERE timestamp IS NOT NULL AND x = ? AND y = ?'''

    @property
    def query_all_by_time(self):
        return '''SELECT id, CAST(strftime('%s', timestamp) AS INT), x, y, color, author FROM place WHERE timestamp IS NOT NULL ORDER BY timestamp, x, y'''

    @property
    def query_all_by_pixel(self):
        return '''SELECT id, CAST(strftime('%s', timestamp) AS INT), x, y, color, author FROM place WHERE timestamp IS NOT NULL ORDER BY x, y, timestamp'''

    @property
    def query_all_count(self):
        return '''SELECT COUNT(*) FROM place WHERE timestamp IS NOT NULL'''

    
class SourceMerged(Source):
    @property
    def name(self):
        return 'merged'

    @property
    def source_file(self):
        return 'merged.sqlite'

    @property
    def query_pixel(self):
        return '''SELECT NULL, timestamp, x, y, color, author FROM placements WHERE x = ? AND y = ? ORDER BY timestamp'''

    @property
    def query_pixel_count(self):
        return '''SELECT COUNT(*) FROM placements WHERE x = ? AND y = ?'''

    @property
    def query_all(self):
        return '''SELECT NULL, timestamp, x, y, color, author FROM placements ORDER BY timestamp, x, y'''

    @property
    def query_all_by_time(self):
        return '''SELECT NULL, timestamp, x, y, color, author FROM placements ORDER BY timestamp, x, y'''

    @property
    def query_all_by_pixel(self):
        return '''SELECT NULL, timestamp, x, y, color, author FROM placements ORDER BY x, y, timestamp'''

    @property
    def query_all_count(self):
        return '''SELECT COUNT(*) FROM placements'''

