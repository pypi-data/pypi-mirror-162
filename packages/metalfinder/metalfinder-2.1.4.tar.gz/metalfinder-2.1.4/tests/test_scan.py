#!/usr/bin/python3

"""Unit tests for metalfinder.scan"""

import os
import pickle
import shutil

import pytest

import metalfinder.scan as mfs


@pytest.mark.parametrize("artist, filepath",
    [('Arch Enemy', 'tests/test_files/arch_enemy.flac'),
     ('Napalm Death', 'tests/test_files/napalm_death.flac')])
def test_get_artist_ok(artist, filepath):
    """Test get_artist() extracts the tag properly"""
    assert artist == mfs.get_artist(None, filepath)


def test_get_artist_no_tag():
    """Test get_artist() returns nothing when there is no artist tag"""
    assert mfs.get_artist(None, 'tests/test_files/no_artist.flac') is None


def test_get_artist_no_header():
    """Test get_artist() returns nothing when there is no FLAC header"""
    artist = mfs.get_artist(None, 'tests/test_files/no_header.flac')
    assert artist is None


def test_write_song_cache(tmpdir):
    """Test function write_song_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = ['1', '2']
    mfs.write_song_cache(data, str(cachedir))
    song_cache_file = os.path.join(str(cachedir), 'song_cache')
    with open(song_cache_file, 'rb') as _cache:
        song_cache = pickle.load(_cache)
        assert song_cache == data


def test_get_song_cache(tmpdir):
    """Test function get_song_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = ['1', '2']
    song_cache_file = os.path.join(str(cachedir), 'song_cache')
    with open(song_cache_file, 'wb') as _cache:
        pickle.dump(data, _cache)
    assert data == mfs.get_song_cache(str(cachedir))


def test_write_artist_cache(tmpdir):
    """Test function write_artist_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = ['1', '2']
    mfs.write_artist_cache(data, str(cachedir))
    artist_cache_file = os.path.join(str(cachedir), 'artist_cache')
    with open(artist_cache_file, 'r', encoding='utf-8') as _cache:
        artist_cache = _cache.read()
        assert artist_cache == '1\n2'


def test_get_artist_cache(tmpdir):
    """Test function get_artist_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = '1\n2'
    artist_cache_file = os.path.join(str(cachedir), 'artist_cache')
    with open(artist_cache_file, 'w', encoding='utf-8') as _cache:
        _cache.write(data)
    assert ['1', '2'] == mfs.get_artist_cache(str(cachedir))


@pytest.mark.parametrize("artist, filename",
    [('Arch Enemy', 'arch_enemy.flac'),
     ('Napalm Death', 'napalm_death.flac')])
def test_scan_dir(artist, filename, tmpdir):
    """Test function scan_dir()"""
    music_dir = tmpdir.join("music_dir")
    music_dir.mkdir()
    origfile = os.path.join('tests/test_files', filename)
    destfile = os.path.join(str(music_dir), filename)
    shutil.copyfile(origfile, destfile)
    mtime = int('1111111111')
    os.utime(destfile, (mtime, mtime))
    good_song_cache = {os.path.join(str(music_dir), filename):
            [1111111111.0, artist]}
    artist_list, new_song_cache = mfs.scan_dir(music_dir, '', [])
    assert artist_list == {artist}
    assert new_song_cache == good_song_cache


@pytest.mark.parametrize("artist, filename",
    [('Arch Enemy', 'arch_enemy.flac'),
     ('Napalm Death', 'napalm_death.flac')])
def test_scan_wrapper(artist, filename, tmpdir):
    """Test wrapper function scan_wrapper()"""
    music_dir = tmpdir.join("music_dir")
    music_dir.mkdir()
    cache_dir = tmpdir.join("cache_dir")
    cache_dir.mkdir()
    origfile = os.path.join('tests/test_files', filename)
    destfile = os.path.join(str(music_dir), filename)
    shutil.copyfile(origfile, destfile)
    artist_list = mfs.scan_wrapper(str(music_dir), str(cache_dir))
    assert artist_list == {artist}


def test_scan_broken_symlink(tmpdir):
    """test that we don't crash on broken symlinks (issues #21)"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    musicdir = tmpdir.join("music")
    musicdir.mkdir()
    musicdir.join("brokensymlink.mp3").mksymlinkto("nonexistent")
    # we don't actually need the result here
    _ = mfs.scan_wrapper(musicdir, cachedir)
