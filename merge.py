#!/usr/bin/env python

import copy
import sqlite3
import sys
import time

import ttystatus

# If similar placements are closer in time than this number of seconds, consider
# them to be duplicates.  /r/place always gave at least a 5 minute cooldown,
# so we'll use that as our window.
DUPLICATE_WINDOW = 300

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

if len(sys.argv) > 1:
    debug = True
    x_list = [int(sys.argv[1])]
    y_list = [int(sys.argv[2])]
else:
    debug = False
    x_list = xrange(0, 1000)
    y_list = xrange(0, 1000)
    
sources = [SourceF(), SourceELFAHBET(), SourceLepon(), SourceWgoodall()]
if not debug:
    dest_conn = sqlite3.connect('merged.sqlite')
    dest_cur = dest_conn.cursor()
    dest_cur.execute('DROP TABLE IF EXISTS placements')
    dest_cur.execute("""
CREATE TABLE placements (
  timestamp INTEGER,
  x INTEGER,
  y INTEGER,
  color INTEGER,
  author INTEGER
)""")
    dest_cur.execute('CREATE INDEX placements_timestamp_idx ON placements(timestamp)')
    dest_cur.execute('CREATE INDEX placements_color_idx ON placements(color)')
    dest_cur.execute('CREATE INDEX placements_author_idx ON placements(author)')
    dest_cur.execute('CREATE INDEX placements_position_idx ON placements(x, y)')

    st = ttystatus.TerminalStatus(period=0.1)
    st.format('%ElapsedTime() %PercentDone(done,total) (%Integer(x),%Integer(y)) [%ProgressBar(done,total)] ETA: %RemainingTime(done,total)')
    st['done'] = 0
    st['total'] = len(x_list) * len(y_list)

for x in x_list:
    if not debug:
        st['x'] = x
    for y in y_list:
        if not debug:
            st['y'] = y
            st.flush()
        for s in sources:
            s.set_pixel(x, y)
            s.next()
            # Some records have null timestamps.  Ignore those.
            while not s.is_done and s.timestamp is None:
                s.next()
        active_sources = [s for s in sources if not s.is_done]
        while len(active_sources) > 0:
            ref = sorted(active_sources, key=lambda s: s.timestamp)[0]
            timestamp = ref.timestamp
            color = ref.color
            author = ref.author
            change_sources = []
            # For each source, if the current placement matches our reference,
            # advance to the next one, because we've now handled this one.
            for s in active_sources:
                if s.color == color and \
                   s.author[:10] == author[:10] and \
                   s.timestamp - timestamp <= DUPLICATE_WINDOW:
                    change_sources.append(s.name)
                    if len(s.author) > author:
                        author = s.author
                    s.next()
            if debug:
                print '{}  {:3} {:3} {:3}  {:16} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)), x, y, color, author, change_sources)
            else:
                dest_cur.execute('INSERT INTO placements VALUES (?, ?, ?, ?, ?)', (timestamp, x, y, color, author))
            active_sources = [s for s in active_sources if not s.is_done]
        if not debug:
            st['done'] += 1
if not debug:
    dest_conn.commit()
    st.finish()
