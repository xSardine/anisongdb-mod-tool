import json

# flask
from flask import Blueprint, render_template, redirect, session, request
from flask import current_app as app

# models
from src.extensions import db
from src.models.songs.song import SongSearchForm, SongUpdateForm, Song
from src.models.songs.link_song_artist import LinkSongArtist
from src.models.artists.line_up import LineUp
from src.models.artists.role_type import RoleType

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query

# ---- Admin UI Anime ---- #
blueprint = Blueprint("link_song_artist", __name__, url_prefix="/songs/")


@blueprint.route("/artist/add/", methods=["POST"])
def link_song_artist():
    # retrieve request body
    request_body = request.get_json()
    id_artist = request_body.get("id_artist", None)
    id_artist_line_up = request_body.get("id_artist_line_up", None)
    id_song = request_body.get("id_song", None)
    id_role_type = request_body.get("id_role_type", None)

    if type(id_role_type) is str:
        if RoleType.query.filter_by(role_type=id_role_type).count() == 1:
            print("found role type")
            id_role_type = RoleType.query.filter_by(role_type=id_role_type).first().id

    if not id_artist_line_up:
        # check if it has a line up anyway
        if int(id_role_type) == 1:
            id_artist_line_up = (
                LineUp.query.filter(LineUp.id_artist == id_artist)
                .order_by(LineUp.id.asc())
                .first()
            )
            id_artist_line_up = id_artist_line_up.id if id_artist_line_up else None
        if not id_artist_line_up:
            id_artist_line_up = None

    try:
        link_song_artist = LinkSongArtist(
            id_song=id_song,
            id_artist=id_artist,
            id_artist_line_up=id_artist_line_up,
            id_role_type=id_role_type,
        )
        db.session.add(link_song_artist)
        db.session.commit()
    except Exception as e:
        print(f"There was an issue adding the artist to the song: {e}")
        return f"There was an issue adding the artist to the song: {e}"

    return json.dumps(link_song_artist.as_dict())


@blueprint.route("artists/<int:id_song_artist>", methods=["DELETE"])
def unlink_song_artist(id_song_artist):
    try:
        link_song_artist = LinkSongArtist.query.get(id_song_artist)
        db.session.delete(link_song_artist)
        db.session.commit()
    except Exception as e:
        return f"There was an issue adding the artist to the song: {e}"

    return json.dumps(link_song_artist.as_dict())
