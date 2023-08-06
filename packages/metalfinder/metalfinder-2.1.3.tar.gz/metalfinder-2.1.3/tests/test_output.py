#!/usr/bin/python3

"""Test the functions in metalfinder.output"""

import os
import datetime

import metalfinder.output as mfo


CONCERT_LIST = [{'artist_id': '1',
                 'datetime': '2022-11-06T20:00:00',
                 'description': 'Concert 1',
                 'id': '12345',
                 'lineup': ['Arch Enemy'],
                 'title': 'Concert 1',
                 'updated': datetime.datetime(2022, 6, 6, 20, 5, 13, 366428),
                 'url': 'https://www.bandsintown.com/e/12345',
                 'venue': {'city': 'Oslo',
                 'name': 'TheFooBar'}},
                {'artist_id': '2',
                 'datetime': '2022-11-07T20:00:00',
                 'description': 'Concert 2',
                 'id': '54321',
                 'lineup': ['Napalm Death', 'Amorphis'],
                 'title': 'Concert 2',
                 'updated': datetime.datetime(2022, 6, 5, 20, 5, 13, 366428),
                 'url': 'https://www.bandsintown.com/e/54321',
                 'venue': {'city': 'Montreal',
                 'name': 'MTelus'}}]


def test_pretty_strings():
    """Test function pretty_strings()"""
    concert = {'id': '1',
               'lineup': ['Arch Enemy'],
               'datetime': '2022-01-01T20:00:00',
               'venue': {'name': 'MTelus',
                         'city': 'Montreal'},
               'description': 'This is a description'}
    formatted_tuple = ('1', 'Arch Enemy', '2022-01-01 20:00', 'MTelus, Montreal',
                       'This is a description', 'https://www.bandsintown.com/e/1')
    assert formatted_tuple == mfo.pretty_strings(concert)


def test_atom(tmpdir):
    """Test function atom()"""
    outdir = tmpdir.join('out')
    outdir.mkdir()
    output = mfo.atom(CONCERT_LIST)
    # We need to write to a file, since this object is a
    # feedgenerator.django.utils.feedgenerator.Atom1Feed object
    with open(str(outdir) + '.atom', 'w', encoding='utf-8') as final:
        output.write(final, 'utf-8')
    with open('tests/test_files/concerts.atom', 'r', encoding='utf-8') as file1:
        valid_atom = file1.read()
        with open(str(outdir) + '.atom', 'r', encoding='utf-8') as file2:
            testfile_atom = file2.read()
            assert valid_atom == testfile_atom


def test_txt():
    """Test function txt()"""
    output = mfo.txt(CONCERT_LIST)
    with open('tests/test_files/concerts.txt', 'r', encoding='utf-8') as file1:
        valid_txt = file1.read()
        assert valid_txt == output


def test_json():
    """Test function _json()"""
    output = mfo._json(CONCERT_LIST)  # pylint: disable=W0212
    with open('tests/test_files/concerts.json', 'r', encoding='utf-8') as file1:
        valid_json = file1.read()
        assert valid_json == output


def test_output_wrapper(tmpdir):
    """Test wrapper function output_wrapper()"""
    outdir = tmpdir.join('out')
    outdir.mkdir()
    output_path = os.path.join(outdir, 'foo.txt')
    mfo.output_wrapper(CONCERT_LIST, output_path)
    with open('tests/test_files/concerts.txt', 'r', encoding='utf-8') as file1:
        valid_txt = file1.read()
        with open(output_path, 'r', encoding='utf-8') as file2:
            output_file = file2.read()
        assert valid_txt == output_file
