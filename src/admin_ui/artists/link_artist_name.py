# flask
from flask import Blueprint, jsonify, redirect, session, request
from flask import current_app as app
import json

# models
from src.extensions import db
from src.models.artists.artist import ArtistSearchForm, ArtistUpdateForm, Artist
from src.models.artists.link_artist_names import LinkArtistName

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query

# ---- Admin UI Anime ---- #
blueprint = Blueprint("link_artist_name", __name__, url_prefix="/artists/")


@blueprint.route("<int:id_artist>/names/", methods=["POST"])
def artist_add_name(id_artist):
    # retrieve request body
    request_body = request.get_json()
    artist_name = request_body["artist_name"]
    original_artist_name = request_body.get("original_artist_name", None)

    # check that artist_name original_artist_name tuple does not already exist
    if (
        LinkArtistName.query.filter_by(
            id_artist=id_artist,
            artist_name=artist_name,
            original_artist_name=original_artist_name,
        ).count()
        > 0
    ):
        return (
            jsonify(
                f"Artist name {artist_name} ({original_artist_name}) already exists for artist {id_artist}"
            ),
            409,
        )

    # get last order
    last_order = (
        LinkArtistName.query.filter_by(id_artist=id_artist)
        .order_by(LinkArtistName.order.desc())
        .first()
    )

    try:
        link_artist_name = LinkArtistName(
            id_artist=id_artist,
            artist_name=artist_name,
            original_artist_name=original_artist_name,
            order=last_order.order + 1 if last_order else 0,
        )
        db.session.add(link_artist_name)
        db.session.commit()
    except Exception as e:
        return f"There was an issue adding the name to the artist: {e}"

    return json.dumps(link_artist_name.as_dict())


@blueprint.route("<int:id_artist>/names/<int:name_id>", methods=["DELETE"])
def artist_remove_name(id_artist, name_id):
    # check that name_id exist for this id_artist
    link_artist_name = LinkArtistName.query.get(name_id)
    if link_artist_name.id_artist != id_artist:
        return (
            jsonify(f"Can't find {name_id} for artist {id_artist}"),
            404,
        )

    # if it's last name of the artist, don't delete it
    if len(Artist.query.get(id_artist).artist_names) == 1:
        return (
            jsonify("Cannot delete the last name of an artist."),
            409,
        )

    # get the order of the name to delete
    order = link_artist_name.order

    # delete the name
    try:
        # decrease the order of all the names with a higher order
        LinkArtistName.query.filter(
            LinkArtistName.id_artist == id_artist, LinkArtistName.order > order
        ).update({"order": LinkArtistName.order - 1})

        # delete the name
        db.session.delete(link_artist_name)
        db.session.commit()
    except Exception as e:
        return (
            jsonify(f"There was an error deleting the name : {e}"),
            500,
        )

    return json.dumps(link_artist_name.as_dict())


@blueprint.route("<int:id_artist>/names/<int:name_id>", methods=["PUT"])
def artist_update_name(id_artist, name_id):
    print(id_artist, name_id)

    # check that name_id exist for this id_artist
    link_artist_name = LinkArtistName.query.get(name_id)
    if link_artist_name.id_artist != id_artist:
        return f"Name {name_id} does not exist for artist {id_artist}"

    # update the name
    request_body = request.get_json()
    artist_name = request_body["artist_name"]
    original_artist_name = request_body.get("original_artist_name", None)

    try:
        link_artist_name.artist_name = artist_name or None
        link_artist_name.original_artist_name = original_artist_name or None
        db.session.commit()
    except Exception as e:
        return f"There was an issue updating the name from the artist: {e}"

    return json.dumps(link_artist_name.as_dict())


@blueprint.route("<int:id_artist>/names/reorder/", methods=["PUT"])
def artist_reorder_names(id_artist):
    request_body = request.get_json()
    orders = request_body.get("order", None)

    if not orders:
        return jsonify({"error": "No order provided"}), 400

    if len(orders) != LinkArtistName.query.filter_by(id_artist=id_artist).count():
        return (
            jsonify(
                {"error": "The number of names does not match the number of orders"}
            ),
            400,
        )

    try:
        for order in orders:
            LinkArtistName.query.filter_by(id=order["id"]).update(
                {"order": order["order"]}
            )
        db.session.commit()
    except Exception as e:
        return f"There was an issue updating the order of the names: {e}"

    return jsonify(orders)
