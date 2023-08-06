#!/usr/bin/python3

"""Test the functions in metalfinder.concerts"""

import os
import pickle

import pytest

import metalfinder.concerts as mfc


def test_has_changed_false():
    """Test has_changed() is False for existing concert"""
    concert = {'id': '102459446', 'title': 'Placeholder'}
    concert_cache = [{'artist_id': '862',
                      'id': '102459446'}]
    concert_is_new = mfc.has_changed(concert_cache, concert)
    assert concert_is_new is False


def test_has_changed_true():
    """Test has_changed() is True for new concert"""
    concert = {'id': '12345', 'title': 'Placeholder'}
    concert_cache = [{'artist_id': '862',
                      'id': '102459446'}]
    concert_is_new = mfc.has_changed(concert_cache, concert)
    assert concert_is_new is True


def test_write_concert_cache(tmpdir):
    """Test function write_concert_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = ['1', '2']
    mfc.write_concert_cache(data, str(cachedir))
    concert_cache_file = os.path.join(str(cachedir), 'concert_cache')
    with open(concert_cache_file, 'rb') as _cache:
        concert_cache = pickle.load(_cache)
        assert concert_cache == data


def test_get_concert_cache(tmpdir):
    """Test function get_concert_cache()"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    data = ['1', '2']
    concert_cache_file = os.path.join(str(cachedir), 'concert_cache')
    with open(concert_cache_file, 'wb') as _cache:
        pickle.dump(data, _cache)
    assert data == mfc.get_concert_cache(str(cachedir))


@pytest.mark.xfail(reason="Test not implemented yet.")
def test_query_bit():
    """Test function query_bit()"""
    # This is hard, and requires mocking requests. TODO!
    assert False


def test_filter_location():
    """Test function filter_location()"""
    concert_list = [{'artist_id': '862',
                     'id': '102459446',
                     'venue': {'city': 'Montreal',
                               'other': 'Foobar'}},
                    {'artist_id': '1',
                     'id': '12345',
                     'venue': {'city': 'Oslo',
                               'other': 'Foobar'}}]
    filtered_list = [{'artist_id': '1',
                      'id': '12345',
                      'venue': {'city': 'Oslo',
                                'other': 'Foobar'}}]
    assert filtered_list == mfc.filter_location(concert_list, 'Oslo')


@pytest.mark.xfail(reason="Test not implemented yet.")
def test_bit():
    """Test wrapper function bit()"""
    # This is hard, and requires mocking requests. TODO!
    assert False
