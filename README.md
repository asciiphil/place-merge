Summary
=======

Merges the change history for the canvas, pixel by pixel.


Usage
=====

Install the NumPy and ttystatus Python modules.

Download files from the google document.

For wgoodall01's, F's, and ELFAHBET_SOOP's SQLite databases, name them:

 * `source-ELFAHBET_SOOP.sqlite`
 * `source-F.sqlite` and
 * `source-wgoodall01.sqlite`

Name lepon01's file:

 * `source-lepon01.csv`

Run `convert-lepon01-csv2sqlite.py` .

Run `add-indexes.sh` .

If you run `merge.py` with an x and y command line parameters, it will
show the merged series of changes for that pixel.  e.g.:

    $ ./merge.py 67 32
    2017-04-01 08:23:32   67  32  15  calltheherd      ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-02 05:39:36   67  32   3  DeepFriedBabeez  ['F']
    2017-04-02 06:32:23   67  32   3  DeepFriedBabeez  ['ELFAHBET_SOOP']

If you run `merge.py` without any parameters, it will write a new database
with the merged data.
