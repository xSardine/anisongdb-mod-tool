# flask
from flask import Blueprint, render_template, redirect, session, request
from flask import current_app as app

# models
from src.extensions import db
from src.models.artists.artist import Artist, deserialize_artist
from src.models.artists.link_artist_names import LinkArtistName
from src.models.artists.line_up import LineUp, deserialize_line_up

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query


# ---- Admin UI Anime ---- #
blueprint = Blueprint("autocomplete", __name__, url_prefix="/autocomplete/")


@blueprint.route("/artists", methods=["GET"])
def autocomplete_artist():
    # get query args
    query_args = get_query_args(request)
    search = query_args.get("search", None)
    limit = query_args.get("limit", 100)

    artists = (
        Artist.query.join(LinkArtistName)
        .filter(
            LinkArtistName.artist_name.ilike(f"%{search}%")
            | LinkArtistName.original_artist_name.ilike(f"%{search}%")
        )
        .limit(limit)
        .all()
    )

    artists = [deserialize_artist(artist, extend_names=True) for artist in artists]

    return artists


@blueprint.route("/line_ups", methods=["GET"])
def autocomplete_line_up():
    query_args = get_query_args(request)
    id_artist = query_args.get("id_artist", None)

    if not id_artist:
        return []

    line_ups = LineUp.query.filter(LineUp.id_artist == id_artist).all()

    return [deserialize_line_up(line_up, extend_members=True) for line_up in line_ups]
