# flake8: noqa:F401

"""The admin_ui module, interacting with the user through form to display and edit data"""
from . import auth, autocomplete
from .anime import anime, link_anime_name
from .artists import artists, link_artist_name, link_artist_line_up
from .songs import songs, link_song_artist
