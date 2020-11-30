# Listlord

> :warning: **This project is still in a pre-alpha state.** Use at your own risk.

Open source software and file-format specification for the creation and 
consumption of universal playlists.

## Format specification

Playlists will be stored in `.list` files. The data will be structured according
to the XML standard for unambiguity, reliability, and universal support. The
text characters should be UTF-8 using Unix-style LF line-endings.

The structure will be as follows:
* `title`: The playlist's title
* `description`: *[Optional]* The playlist's description limited to 140 characters.
* `image`: *[Optional]*
  * `href`: *[Optional]* Web link to the playlist's desired image file.
  * `bytes`: *[Optional]* HTML-style binary image src.
* `author`: *[Optional]*
  * `name`: The author's name (preferably FIRST LAST but anything goes)
  * `email`: *[Optional]* The author's email if they want people to be able to get in touch with them.
  * `website`: *[Optional]* The author's website. Could be social media or even a github repo with their other playlists. Again, anything goes but there is an unfortunate potential for troll-links/spam.
* `tracks`:
  * `shuffle` (bool): *[Optional (Defaults to false)]* If true, this playlist is meant to be heard in random order. If false, this playlist has a specific order that the author intended to be preserved.
  * `track`: *[Repeatable]*
    * `title`: Track's title
    * `artists`:
      * `artist`: *[Repeatable]*
        * `name`: The artist's name
        * `mbid`: *[Optional]* The artist's MusicBrainz ID
    * `album`:
        * `name`: The album's name
        * `mbid`: *[Optional]* The album's release group MusicBrainz ID
    * `mbid`: *[Optional]* The track's recording MusicBrainz ID
    * `duration`: *[Optional]* The track's duration in seconds
