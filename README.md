Summary
=======

Merges the change history for the canvas, pixel by pixel.

The entire merge process will use about 8GB of disk space.  The result is
a roughly 1.6GB SQLite database with roughly 16 million pixel placements.


Usage
=====

First, install the [NumPy][] and [ttystatus][] Python modules.  You'll
also need [PRAW][] and/or [BeautifulSoup][] if you want to use Reddit's
/r/place flair to correlate the various dataset's timestamps.  (NB: You
want to do that; it turns a gigantic mess into a somewhat-smaller mess.)

  [NumPy]: http://www.numpy.org/
  [ttystatus]: http://liw.fi/ttystatus/
  [PRAW]: https://praw.readthedocs.io/
  [BeautifulSoup]: https://www.crummy.com/software/BeautifulSoup/

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

Now you need to pull some data from Reddit.  The timestamps in people's
datasets are all over the place, for reasons ranging from clock skew to
server lag to client lag.  Reddit puts the location, color, and timestamp
of each person's last-placed pixel in their flair for /r/place, so we can
use that data to get canonical timestamps for specific placements and then
use those placements to adjust each dataset's timing.

The easy way to do this is to go to Reddit in your browser, open a
submission page, save it, and run `import-place-flair.py` on it.  You
should do this with several pages, with as many as comments on each as
possible, to get as many different flairs as you can.

The more involved (but more thorough) way is to use the Reddit API to
fetch large numbers of flairs from /r/place posts.  For that, you'll need
to set up PRAW authentication.  Follow the [PRAW authentication
instructions][PRAW-auth] to get a client_id and client_secret.  Put those
along with your Reddit username and password into a `praw.ini`, like this:

    [DEFAULT]
    client_id=abcde...
    client_secret=123ghi...
    username=phil_g
    password=hunter2

  [PRAW-auth]: https://praw.readthedocs.io/en/latest/getting_started/authentication.html

Now, run `fetch-place-flair.py` and wait for it to pull people's flairs.
Check its `--help` parameter; you can use its command line parameters to
pull more or less data, depending on how long you want it to run.

After you've imported or fetched some flair, run `correlate-timestamps.py`
to figure out adjustments to the dataset's timestamps.

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
with the merged data.  This takes a couple of hours on the author's system.


Utilities
=========

The `make-image.py` script runs the source datasets through all of their
changes to make a final image.  It needs the Python Imaging Library
installed.

The `make-video.py` script does more or less the same thing, but creates a
timelapse video of each dataset.  It needs [ffmpeg][] to be installed and
in the `$PATH`.

  [ffmpeg]: https://ffmpeg.org
  
