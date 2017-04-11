#!/bin/sh

sqlite3 source-ELFAHBET_SOOP.sqlite "CREATE INDEX placements_position_idx ON placements(x, y)"
sqlite3 source-F.sqlite "CREATE INDEX placements_position_idx ON placements(x, y)"
sqlite3 source-lepon01.sqlite "CREATE INDEX placements_recieved_on_idx ON placements(recieved_on)"
sqlite3 source-lepon01.sqlite "CREATE INDEX placements_author_idx ON placements(author)"
sqlite3 source-lepon01.sqlite "CREATE INDEX placements_color_idx ON placements(color)"
sqlite3 source-lepon01.sqlite "CREATE INDEX placements_position_idx ON placements(x, y)"
sqlite3 source-wgoodall01.sqlite "CREATE INDEX place_color_idx ON place(color)"
sqlite3 source-wgoodall01.sqlite "CREATE INDEX place_author_idx ON place(author)"
sqlite3 source-wgoodall01.sqlite "CREATE INDEX place_position_idx ON place(x, y)"
