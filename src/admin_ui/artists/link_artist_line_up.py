# flask
from flask import Blueprint, jsonify, redirect, session, request
from flask import current_app as app
import json

# models
from src.extensions import db
from src.models.artists.artist import ArtistSearchForm, ArtistUpdateForm, Artist
from src.models.songs.link_song_artist import LinkSongArtist
from src.models.artists.line_up import LineUp
from src.models.artists.link_artist_line_up import LinkArtistLineUp

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query

# ---- Admin UI Anime ---- #
blueprint = Blueprint("link_artist_line_up", __name__, url_prefix="/")


def automatically_populate_new_line_up(id_artist, id_line_up, automatic=False):
    message = """
    <h3 class="title is-5 is-spaced">Songs</h3>\n
    """
    message += "<ul>"
    for linked_song in LinkSongArtist.query.filter(
        LinkSongArtist.id_artist == id_artist
    ).all():
        message += f"""<li>
        <a href="/songs/{linked_song.id_song}" target="_blank">{linked_song.song.song_name}</a>
        </li>\n"""
        if automatic:
            linked_song.id_artist_line_up = id_line_up
    message += "</ul>"
    message += "<br>"

    message += """
    <h3 class="title is-5 is-spaced">Groups</h3>\n
    """
    message += "<ul>"
    for linked_artist in LinkArtistLineUp.query.filter(
        LinkArtistLineUp.id_member == id_artist
    ).all():
        message += f"""<li>
        <a href="/artists/{linked_artist.id_group}" target="_blank">{linked_artist.group.artist_names[0].artist_name}</a>
        </li>\n"""
        if automatic:
            linked_artist.id_member_line_up = id_line_up
    message += "</ul>"
    message += "<br>"

    return message


def fallback_to_id_line_up(id_line_up, fallback_id_line_up, automatic=False):
    message = """
    <h3 class="title is-5 is-spaced">Songs</h3>\n
    """
    message += "<ul>"
    for linked_song in LinkSongArtist.query.filter(
        LinkSongArtist.id_artist_line_up == id_line_up
    ).all():
        message += f"""<li>
        <a href="/songs/{linked_song.id_song}" target="_blank">{linked_song.song.song_name}</a>
        </li>\n"""
        if automatic:
            linked_song.id_artist_line_up = fallback_id_line_up
    message += "</ul>"
    message += "<br>"

    message += """
    <h3 class="title is-5 is-spaced">Groups</h3>\n
    """
    message += "<ul>"
    for linked_artist in LinkArtistLineUp.query.filter(
        LinkArtistLineUp.id_member_line_up == id_line_up
    ).all():
        message += f"""<li>
        <a href="/artists/{linked_artist.id_group}" target="_blank">{linked_artist.group.artist_names[0].artist_name}</a>
        </li>\n"""
        if automatic:
            linked_artist.id_member_line_up = fallback_id_line_up
    message += "</ul>"
    message += "<br>"

    return message


@blueprint.route("/artists/<int:id_artist>/line_ups/", methods=["POST"])
def add_line_up(id_artist):
    # check existing line ups for that artist
    existing_line_ups = LineUp.query.filter(LineUp.id_artist == id_artist).all()

    new_line_up = LineUp(id_artist=id_artist)
    db.session.add(new_line_up)
    db.session.flush()

    message = f"""
    <h1 class="title is-4 is-spaced">Server's feedback for line up #{new_line_up.id} addition</h1>\n
    """

    # if there are no line ups yet : default everything to new line up
    if len(existing_line_ups) == 0:
        message += f"""Automatically swapping from {id_artist} to {new_line_up.id} in all these songs and groups :<br><br>\n"""
        message += automatically_populate_new_line_up(
            id_artist, new_line_up.id, automatic=True
        )
    else:
        message += """There are already existing line ups, please swap manually for all songs and groups that should be linked to this new line up :<br><br>\n"""
        message += automatically_populate_new_line_up(
            id_artist, new_line_up.id, automatic=False
        )

    db.session.commit()

    return jsonify({"new_line_up": new_line_up.as_dict(), "feedback": message})


@blueprint.route("/line_ups/<int:id_line_up>", methods=["DELETE"])
def remove_line_up(id_line_up):
    # check if there are still members in the line up

    print("deleting", id_line_up)

    line_up = LineUp.query.get(id_line_up)

    if line_up.members:
        return (
            jsonify(
                {"error": f"Line up {id_line_up} still has members, can't delete it"}
            ),
            400,
        )

    # check if there are other line ups for that artist : id_artist = artist.id and id_line_up != line_up.id
    artist = Artist.query.get(line_up.id_artist)
    other_line_ups = LineUp.query.filter(
        LineUp.id_artist == artist.id, LineUp.id != line_up.id
    ).all()

    message = f"""
    <h1 class="title is-4 is-spaced">Server's feedback for line up #{id_line_up} removal</h1>\n
    """
    # if there is 0 line up, there is no other line up for that artist, all FK should go to None: default behaviour
    if len(other_line_ups) == 0:
        fallback_id_line_up = None
        message += f"""Automatically swapping from {id_line_up} to {fallback_id_line_up} in all these songs and groups : <br><br>\n"""
        message += fallback_to_id_line_up(
            id_line_up, fallback_id_line_up, automatic=True
        )
    # if there is 1 line ups, all FK should default to the remaining line up after deletion :
    if len(other_line_ups) == 1:
        fallback_id_line_up = other_line_ups[0].id
        message += f"""Automatically swapping from {id_line_up} to {fallback_id_line_up} in all these songs and groups : <br><br>\n"""
        message += fallback_to_id_line_up(
            id_line_up, fallback_id_line_up, automatic=True
        )
    # if there is more than 1 line up, TODO : ambiguous, should ask which one to default to
    elif len(other_line_ups) > 1:
        fallback_id_line_up = other_line_ups[0].id
        message += f"""There is more than 1 remaining line up after deletion, can not automatically link a fallback line up, please check manually, currently defaulting to line up #{fallback_id_line_up} for these :<br><br>\n"""
        message += fallback_to_id_line_up(
            id_line_up, fallback_id_line_up, automatic=True
        )

    # else possible to delete
    db.session.delete(line_up)
    db.session.commit()

    return jsonify({"deleted_line_up": line_up.as_dict(), "feedback": message})


@blueprint.route("/line_ups/<int:id_line_up>", methods=["POST"])
def add_line_up_member(id_line_up):
    # get id_artist to add from body
    request_body = request.get_json()
    id_member = request_body.get("id_member", None)
    id_member_line_up = request_body.get("id_member_line_up", None)
    id_role_type = request_body.get("id_role_type", 1)

    # Check if (id_member, id_member_line_up) is already in the line-up
    line_up = LineUp.query.get(id_line_up)

    if not id_member_line_up:
        # check if it has a line up anyway
        if int(id_role_type) == 1:
            id_member_line_up = (
                LineUp.query.filter(LineUp.id_artist == id_member)
                .order_by(LineUp.id.asc())
                .first()
            )
            id_member_line_up = id_member_line_up.id if id_member_line_up else None
        if not id_member_line_up:
            id_member_line_up = None

    if any(
        member.id_member == id_member and member.id_member_line_up == id_member_line_up
        for member in line_up.members
    ):
        error_message = f"Artist {id_member} is already in line-up {id_line_up} with id {id_member_line_up}"
        return jsonify({"error": error_message}), 400

    # add new member to line up
    new_member = LinkArtistLineUp(
        id_member=id_member,
        id_member_line_up=id_member_line_up,
        id_role_type=id_role_type,
        id_group=line_up.id_artist,
        id_group_line_up=line_up.id,
    )

    print(new_member.as_dict())

    db.session.add(new_member)
    db.session.commit()

    print(new_member.as_dict())

    return jsonify(new_member.as_dict())


@blueprint.route("/line_ups/members/<int:id_link_artist_line_up>", methods=["DELETE"])
def remove_line_up_member(id_link_artist_line_up):
    link_artist_line_up = LinkArtistLineUp.query.get(id_link_artist_line_up)
    db.session.delete(link_artist_line_up)
    db.session.commit()

    return jsonify(link_artist_line_up.as_dict())
