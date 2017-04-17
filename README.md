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

Import each dataset with the `import-source.py` script.  Use its `-s` and
`-n` parameters.  (See `import-source.py --help` for their descriptions.)
Use the following schemas:

| Dataset         | Schema                |
|-----------------|-----------------------|
| ELFAHBET_SOOP   | place-scraper-swapped |
| F               | place-scraper-swapped |
| teaearlgraycold | place-scraper         |
| wgoodall01      | wgoodall01            |
| lepon01         | moustacheminer        |

At this point, you can run `merge.py` with x and y command line parameters
to show the merged series of changes for that pixel.  e.g.:

    $ ./merge.py -p 67 32
    2017-04-01 08:23:29   67  32  15  calltheherd      teaearlgraycold
               08:23:31                              + lepon01
               08:23:32                              + ELFAHBET_SOOP
               08:23:32                              + F
    2017-04-02 04:25:10   67  32   3                   wgoodall01
    2017-04-02 05:39:36   67  32   3  DeepFriedBabeez  F
    2017-04-02 06:32:23   67  32   3  DeepFriedBabeez  ELFAHBET_SOOP
    2017-04-02 07:42:11   67  32   3  DeepFriedBabeez  teaearlgraycold
    00h01m18s 100 % [##############################################] ETA: 00h00m00s

This is useful for debugging and sanity-checking.

If you run `merge.py` without any parameters, it will write a new database
with the merged data.  This takes an hour or so on the author's system.


Utilities
=========

The `make-image.py` script runs the source datasets through all of their
changes to make a final image.  It needs the Python Imaging Library
installed.

The `make-video.py` script does more or less the same thing, but creates a
timelapse video of each dataset.  It needs [ffmpeg][] to be installed and
in the `$PATH`.

  [ffmpeg]: https://ffmpeg.org
  
