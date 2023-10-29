# flask
from flask import Blueprint, jsonify, redirect, session, request
from flask import current_app as app
import json

# models
from src.extensions import db
from src.models.anime.link_anime_names import LinkAnimeName

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query

# ---- Admin UI Anime ---- #
blueprint = Blueprint("link_anime_name", __name__, url_prefix="/anime/")


@blueprint.route("<int:id_anime>/names/<int:id_name>", methods=["PUT"])
def anime_update_name(id_anime, id_name):
    print(id_anime, id_name)

    # check that id_name exist for this id_anime
    link_anime_name = LinkAnimeName.query.get(id_name)
    if link_anime_name.id_anime != id_anime:
        return f"Name {id_name} does not exist for anime {id_anime}"

    # update the name
    request_body = request.get_json()
    original_anime_name = request_body.get("original_anime_name", None)

    print(original_anime_name)
    print(link_anime_name.as_dict())

    try:
        link_anime_name.original_anime_name = original_anime_name or None
        db.session.commit()
    except Exception as e:
        return f"There was an issue updating the name from the anime: {e}"

    return json.dumps(link_anime_name.as_dict())
