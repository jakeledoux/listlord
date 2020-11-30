#!/bin/python3

""" Listlord: Open source software and file-format specification for the
    creation and consumption of universal playlists.

    Jake Ledoux, 2020
    contactjakeledoux@gmail.com
    https://jakeledoux.com
"""

import os
import spotipy
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

LISTLORD_VERSION = '0.0.1'
SP_CLIENT_ID = 'a3cafa0783964e33b45fd7662cdf909b'
SP_CLIENT_SECRET = '14f1117a0fcc477482f8a6cd78e6248f'
spotify = None


def init_spotify():
    global spotify
    if spotify is None:
        spotify = spotipy.Spotify()
    return spotify

def filename_encode(text):
    keep_chars = ('_', '-')
    filename = ''.join([c if (c.isalnum() or c in keep_chars) else ' '
                        for c in text])
    filename = '_'.join(filename.split())
    return filename


def spotify_to_dict(playlist_uri):
    spotify = init_spotify()


def XML_from_dict(playlist: dict):
    XML_playlist = Element('ListLordPlaylist', version=LISTLORD_VERSION)
    for key, value in playlist.items():
        elem = Element(key)
        if key == 'tracklist':
            elem.set('shuffle', str(value.get('shuffle', False)).lower())
            for track in value.get('tracks', []):
                track_elem = Element('track')
                for track_key, track_value in track.items():
                    if track_key == 'mbid':
                        track_elem.set('mbid', track_value)
                    elif track_key == 'artists':
                        artists_elem = Element('artists')
                        for artist in track_value:
                            artist_elem = Element('artist', **artist)
                            artists_elem.append(artist_elem)
                        track_elem.append(artists_elem)
                    elif track_key == 'album':
                        album_elem = Element('album', **track_value)
                        track_elem.append(album_elem)
                    else:
                        track_sub_elem = Element(track_key)
                        track_sub_elem.text = str(track_value)
                        track_elem.append(track_sub_elem)
                elem.append(track_elem)
        else:
            if type(value) is str:
                elem.text = value
            elif type(value) is dict:
                elem.attrib = value
        XML_playlist.append(elem)
    return XML_playlist


def write_XML(playlist: Element, filename=None):
    filename = filename or \
            f'{filename_encode(playlist.find("title").text)}.list'
    with open(filename, 'w') as f:
        xml_string = tostring(playlist, encoding='unicode', method='xml')
        f.write(xml_string)

# DEBUG SAMPLE DATA ###########################################################
playlist = {
    'title': 'Daydream Theater',
    'description': 'Dream Theater at their happiest.',
    'author': {
        'name': 'Jake Ledoux',
        'email': 'contactjakeledoux@gmail.com',
        'website': 'https://github.com/jakeledoux/playlists'
    },
    'tracklist': {
        'shuffle': True,
        'tracks': [
            {
                'title': 'Behind the Veil',
                'artists': [{'name': 'Dream Theater',
                             'mbid': '28503ab7-8bf2-4666-a7bd-2644bfc7cb1d'}],
                'album': {'name': 'Dream Theater',
                          'mbid': '1b537b55-6543-436e-b569-91fc789eff43'},
                'mbid': '1fe57f44-aa27-4639-83ed-a305b0ccadca',
                'duration': 412
            },
            {
                'title': 'A Rite of Passage',
                'artists': [{'name': 'Dream Theater',
                             'mbid':'28503ab7-8bf2-4666-a7bd-2644bfc7cb1d'}],
                'album': {'name': 'Black Clouds & Silver Linings',
                          'mbid': 'ba5ef564-b2f8-3bb5-9d8f-57828cfa767c'},
                'mbid': 'b5cc94ec-e1c1-4dba-aa7f-135ce57e7931',
                'duration': 516
            }
        ]
    }
}

playlist = spotify_to_dict('spotify:playlist:48623M5bfynlI4USZGpVVs')
from pprint import pprint
pprint(playlist)
