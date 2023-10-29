# flask
from flask import Blueprint, render_template, redirect, session, request
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
blueprint = Blueprint("artists", __name__, url_prefix="/artists/")


def filter_artists(
    query: Query,
    artist_name: str = None,
    sort_by: str = "id",
    order: str = "asc",
    **unfilteredArgs: any,
) -> Query:
    """
    Filter a query on artists depending on query args filters. It include filters from different tables.

    Parameters
    ----------
    query : SQLAlchemy query
        The query to filter
    artist_name : str
        The name of the artist to filter on
    **unfilteredArgs : any
        Other args that are not used for filtering

    Returns
    -------
    SQLAlchemy query
        The filtered query
    """

    if artist_name:
        query = query.join(LinkArtistName)
        query = query.filter(
            LinkArtistName.artist_name.ilike(f"%{artist_name}%")
            | LinkArtistName.original_artist_name.ilike(f"%{artist_name}%")
        )

    # sorting
    # Check if the provided sort_by is a valid attribute of SiteGeneration
    if hasattr(Artist, sort_by) and not sort_by.startswith("_"):
        query = query.order_by(getattr(getattr(Artist, sort_by), order)())

    return query


def deserialize_artist(artist):
    deserialized_artist = artist.as_dict()
    deserialized_artist["artist_names"] = []
    # ordered by name.id
    for artist_name in sorted(artist.artist_names, key=lambda x: x.order):
        deserialized_artist["artist_names"].append(artist_name.as_dict())
        deserialized_artist["artist_names"][-1].pop("id_artist")

    deserialized_artist["artist_type"] = artist.artist_type.artist_type
    return deserialized_artist


@blueprint.route("/", methods=["GET", "POST"])
def artists_read():
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    query_args = get_query_args(request)

    form = ArtistSearchForm(**query_args)
    # if form is submitted, search artist in database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        form_data["page"] = 1

        try:
            return redirect(populate_url_with_args("/artists/", form_data))
        except Exception as e:
            return f"There was an issue performing the search: {e}"

    else:
        print("form not validated : ", form.errors)

    # get filtered artists from database
    query = db.session.query(Artist)
    query = filter_artists(query, **query_args)
    artists = query.all()

    # get total pages
    total_pages = len(artists) // query_args["page_size"] + 1

    # paginate artists
    artists = artists[
        (query_args["page"] - 1)
        * query_args["page_size"] : query_args["page"]
        * query_args["page_size"]
    ]

    deserialized_artists = [deserialize_artist(artist) for artist in artists]
    # TODO find a better way to swap order
    for artist in deserialized_artists:
        artist["artist_name"] = (
            artist.pop("artist_names")[0]["artist_name"]
            if artist["artist_names"]
            else ""
        )
        artist["artist_disambiguation"] = artist.pop("artist_disambiguation")

    # render template w/ artists
    return render_template(
        "artists/read.jinja2",
        form=form,
        artists=deserialized_artists,
        current_page=query_args["page"],
        total_pages=total_pages,
        username=session["username"],
    )


@blueprint.route("create/", methods=["GET", "POST"])
def artist_create():
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    form = ArtistUpdateForm()

    # if form is submitted, add artist to database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        try:
            # validate args for model
            validate_sqla_object(Artist, form_data)
            artist = Artist(**form_data)
            # update artist in database
            db.session.add(artist)
            db.session.commit()
            return redirect(f"/artists/{artist.id}")
        except ValueError as e:
            args = e.args[0]
            if "query" in args:
                for field, error in args["query"].items():
                    form[field].errors.extend(error)
            return render_template(
                "artists/update.jinja2",
                form=form,
                username=session["username"],
            )
        except Exception as e:
            return f"There was an issue creating your artist: {e}"

    return render_template(
        "artists/create.jinja2",
        form=form,
        username=session["username"],
    )


@blueprint.route("<int:id_artist>/", methods=["GET", "POST"])
def artist_update(id_artist):
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    # Initiliaze form with current artist data
    artist = Artist.query.get_or_404(id_artist)
    form = ArtistUpdateForm(obj=artist)

    # if form is submitted, add artist to database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        try:
            # validate args for model
            validate_sqla_object(Artist, form_data)
            # update artist in database
            db.session.query(Artist).filter_by(id=id_artist).update({**form_data})
            db.session.commit()
            return redirect(f"/artists/{id_artist}")
        except ValueError as e:
            args = e.args[0]
            if "query" in args:
                for field, error in args["query"].items():
                    form[field].errors.extend(error)
            return render_template(
                "artists/update.jinja2",
                form=form,
                artist=artist,
                username=session["username"],
            )
        except Exception as e:
            print(e)
            return f"There was an issue editing your artist: {e}"

    # render template w/ artists
    return render_template(
        "artists/update.jinja2",
        form=form,
        artist=artist,
        username=session["username"],
    )


@blueprint.route("<int:id_artist>", methods=["POST"])
def artist_delete(id_artist):
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    # delete artist from database
    try:
        db.session.query(Artist).filter_by(id=id_artist).delete()
        db.session.commit()
    except Exception as e:
        return f"There was an issue deleting your artist: {e}"

    return redirect("/artists")
