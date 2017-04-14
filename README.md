Summary
=======

Merges the change history for the canvas, pixel by pixel.

The entire merge process will use about 8GB of disk space.  The result is
a roughly 1.6GB SQLite database with roughly 16 million pixel placements.


Usage
=====

First, install the NumPy and ttystatus Python modules.

Next, download the datasets from the Google document, plus
[teaearlgraycold's dataset][teaearlgray].  These scripts currently know
how to deal with data from ELFAHBET_SOOP, F, lepon01, teaearlgraycold, and
wgoodall01.

  [teaearlgray]: https://www.reddit.com/r/PlaceDevs/comments/634nzu/_/dfyq6m8/?context=3

For wgoodall01's, F's, teaearlgraycold's and ELFAHBET_SOOP's SQLite
databases, name them:

 * `source-ELFAHBET_SOOP.sqlite`
 * `source-F.sqlite`
 * `source-teaearlgraycold.sqlite` and
 * `source-wgoodall01.sqlite`

Name lepon01's file:

 * `source-lepon01.csv`

Run `convert-lepon01-csv2sqlite.py` .  This converts lepon01's CSV file
into an SQLite database that's easier to work with.

Run `add-indexes.sh` .  This adds some indexes that make things work a
little better.

Run `unpack.py` .  This combines data from all of the source datasets into
a single, non-consolidated SQLite database.  It also takes the cached
bitmaps from the board-place API endpoint and creates synthetic pixel
placements from them, so the merge process will have uniform data to work
with.  This takes about half an hour on the author's system.

At this point, you can run `merge.py` with x and y command line parameters
to show the merged series of changes for that pixel.  e.g.:

    $ ./merge.py 67 32
    2017-04-01 08:23:32   67  32  15  calltheherd      ELFAHBET_SOOP
               08:23:32                              + F
               08:23:32                              + lepon01
    2017-04-02 05:39:36   67  32   3  DeepFriedBabeez  F
    2017-04-02 06:32:23   67  32   3  DeepFriedBabeez  ELFAHBET_SOOP

This is useful for debugging and sanity-checking.

If you run `merge.py` without any parameters, it will write a new database
with the merged data.  This takes about 40 minutes on the author's system.


Utilities
=========

The `make-image.py` script runs the source datasets through all of their
changes to make a final image.  It needs the Python Imaging Library
installed.

The `make-video.py` script does more or less the same thing, but creates a
timelapse video of each dataset.  It needs [ffmpeg][] to be installed and
in the `$PATH`.

  [ffmpeg]: https://ffmpeg.org
  
