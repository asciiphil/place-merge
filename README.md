Merges the change history for the canvas, pixel by pixel.

Install the ttystatus Python module.

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
    2017-04-01 06:36:22   67  32  15  Fluff3h          ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-01 17:44:40   67  32   7  elisaxo          ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-02 22:37:16   67  32  15  BookerCx         ['F']
    2017-04-02 23:11:20   67  32  15  Crisk1           ['lepon01']
    2017-04-03 05:04:46   67  32   3  Vapelo           ['F', 'ELFAHBET_SOOP']
    2017-04-03 05:05:50   67  32   3  Wamadahama       ['F', 'ELFAHBET_SOOP']
    2017-04-03 05:56:10   67  32  14  lowis44          ['F', 'ELFAHBET_SOOP']
    2017-04-03 05:56:36   67  32   3  Fargohead        ['F', 'ELFAHBET_SOOP']
    2017-04-03 06:42:06   67  32  15  tonytony87       ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-03 06:42:38   67  32   3  Wow4DWow         ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-03 06:46:40   67  32   3  kittypryde123    ['F', 'ELFAHBET_SOOP', 'lepon01']
    2017-04-03 16:19:10   67  32   1  MikeCodesThings  ['ELFAHBET_SOOP']

If you run `merge.py` without any parameters, it will write a new database
with the merged data.
