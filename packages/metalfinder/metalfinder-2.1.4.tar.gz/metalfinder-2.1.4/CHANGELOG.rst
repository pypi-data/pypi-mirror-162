Changelog
=========

metalfinder 2.1.4 (20220807)
----------------------------

* fix: make sure the testsuite doesn't leave files in the CWD.


metalfinder 2.1.3 (20220807)
----------------------------

* fix: fix crashes on files mutagen can't scan.
* add: more tests for a more comprehensive testsuite.


metalfinder 2.1.2 (20220609)
----------------------------

* fix: fix problem with cache_dir in some tests.


metalfinder 2.1.1 (20220609)
----------------------------

* change: remove pyxdg dependency, as it's not needed anymore.


metalfinder 2.1.0 (20220607)
----------------------------

* add: basic testsuite.


metalfinder 2.0.0 (20220528)
----------------------------

**Breaking Changes:** the format of ``XDG_CACHE_HOME/metalfinder/song_cache`` has
changed and it should be deleted, otherwise you'll get a ``KeyError`` error.

* fix: split artist names on '/', '+' and '&' even when using an external
  artist list.
* fix: don't crash when a file that has previously been scanned is deleted.


metalfinder 1.2.0 (20220527)
----------------------------

* change: rename --cache to --cache-dir
* fix: handle broken symlinks gracefully
* fix: don't crash when an artist is removed from the scanned directory
* add: implement METALFINDER_BIT_APPID environment variable
* add: make it possible to run using an externally generated artist list
* add: make it possible to run using "python3 -m metalfiner"


metalfinder 1.1.1 (20220519)
----------------------------

* fix: stop crashes for versions of requests earlier than 2.27


metalfinder 1.1.0 (20220519)
----------------------------

* add: implement event cache


metalfinder 1.0.2 (20220510)
----------------------------

* modified: general improvements to Bandsintown API logic
* fix: extract artists from MP3 files properly
* fix: update cache when files are removed


metalfinder 1.0.1 (20220509)
----------------------------

* fix: split artist names on '/', '+' and '&'


metalfinder 1.0.0 (20220507)
----------------------------

* Initial release
