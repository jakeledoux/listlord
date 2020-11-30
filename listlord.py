#!/bin/python3

""" Listlord: Open source software and file-format specification for the
    creation and consumption of universal playlists.

    Jake Ledoux, 2020
    contactjakeledoux@gmail.com
    https://jakeledoux.com
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from xml.etree.ElementTree import Element, fromstring, tostring

LISTLORD_VERSION = '0.0.1'
SPOTIFY_CLIENT_ID = 'a3cafa0783964e33b45fd7662cdf909b'
SPOTIFY_CLIENT_SECRET = '14f1117a0fcc477482f8a6cd78e6248f'
SPOTIFY = None
SP_SCOPE = ' '.join(('playlist-read-private',  'playlist-modify-private',
                     'playlist-modify-public'))


def init_spotify():
    global SPOTIFY
    global SP_SCOPE
    if SPOTIFY is None:
        SPOTIFY = spotipy.Spotify(
            auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                      client_secret=SPOTIFY_CLIENT_SECRET,
                                      redirect_uri='http://0.0.0.0',
                                      scope=SP_SCOPE)
        )
    return SPOTIFY


def filename_encode(text):
    keep_chars = ('_', '-')
    filename = ''.join([c if (c.isalnum() or c in keep_chars) else ' '
                        for c in text])
    filename = '_'.join(filename.split())
    return filename


def spotify_to_dict(playlist_uri):
    sp = init_spotify()
    playlist = sp.playlist(playlist_uri)

    pl_json = {
        'title': playlist.get('name'),
        'tracklist': {'shuffle': False},
        'author': {
            'name': playlist['owner']['display_name'],
            'website': playlist['owner']['external_urls']['spotify']
        }
    }
    if (desc := playlist.get('description')):
        pl_json['description'] = desc
    if (images := playlist.get('images')):
        pl_json['image'] = {'href': images[0]['url']}

    tracklist = list()
    # TODO: Get ALL tracks when tracklist > 100
    for track in playlist['tracks']['items']:
        track = track['track']
        track_json = {
            'title': track['name'],
            'duration': track['duration_ms'] // 1000,
            'album': {'name': track['album']['name']},
            'artists': [{'name': artist['name']} for artist in track['artists']]
        }
        tracklist.append(track_json)
    pl_json['tracklist']['tracks'] = tracklist
    return pl_json


def dict_to_XML(playlist: dict):
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


def load_XML(filename: str):
    with open(filename, 'r') as f:
        XML_playlist = fromstring(f.read())
    return XML_playlist


def write_XML(playlist: Element, filename=None):
    filename = filename or \
            f'{filename_encode(playlist.find("title").text)}.list'
    with open(filename, 'w') as f:
        xml_string = tostring(playlist, encoding='unicode', method='xml')
        f.write(xml_string)
    return filename


def XML_to_spotify(playlist: Element):
    sp = init_spotify()
    user_ID = sp.current_user()['id']
    desc = desc_elem.text \
        if (desc_elem := playlist.find('description')) is not None else ''
    playlist_ID = sp.user_playlist_create(
        user_ID, playlist.find('title').text,
        description=desc
    )['id']
    tracklist = list()
    for track in playlist.find('tracklist'):
        title = track.find('title').text
        album = track.find('album').get('name')
        duration = int(track.find('duration').text)
        primary_artist = track.find('artists')[0].get('name')
        artist_names = [a.get('name') for a in track.find('artists')]
        results = sp.search(q=f'{title} {primary_artist}')

        # Score results
        scores = list()
        for result in results['tracks']['items']:
            score = 0
            if result['name'] == title:
                score += 10
            if result['album']['name'] == album:
                score += 10
            for artist in result['artists']:
                if artist['name'] in artist_names:
                    score += 10
            score -= abs(duration - (result['duration_ms'] // 1000))
            scores.append((score, result['id']))
        tracklist.append(sorted(scores, key=lambda x: x[0], reverse=True)[0][1])

    sp.user_playlist_add_tracks(user_ID, playlist_ID, tracklist)

