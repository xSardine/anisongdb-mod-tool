# flask
from flask import Blueprint, render_template, redirect, session, request
from flask import current_app as app

# models
from src.extensions import db
from src.models.anime.anime import (
    AnimeSearchForm,
    deserialize_anime,
    AnimeUpdateForm,
    Anime,
)
from src.models.anime.link_anime_tags import LinkAnimeTag
from src.models.anime.link_anime_genres import LinkAnimeGenre
from src.models.anime.link_anime_names import LinkAnimeName
from src.models.artists.link_artist_names import LinkArtistName
from src.models.songs.link_song_artist import LinkSongArtist
from src.models.artists.link_artist_line_up import LinkArtistLineUp

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# Typing helpers
from sqlalchemy.orm import Query


# ---- Admin UI Anime ---- #
blueprint = Blueprint("anime", __name__, url_prefix="/anime/")


def filter_anime(
    query: Query,
    anime_name: str = None,
    sort_by: str = "id",
    order: str = "asc",
    **unfilteredArgs: any,
) -> Query:
    """
    Filter a query on anime depending on query args filters. It include filters from different tables.

    Parameters
    ----------
    query : SQLAlchemy query
        The query to filter
    anime_name : str
        The name of the anime to filter on
    **unfilteredArgs : any
        Other args that are not used for filtering

    Returns
    -------
    SQLAlchemy query
        The filtered query
    """

    if anime_name:
        query = query.filter(
            Anime.anime_expand_name.ilike(f"%{anime_name}%")
            | Anime.original_anime_expand_name.ilike(f"%{anime_name}%")
            | Anime.anime_jp_name.ilike(f"%{anime_name}%")
            | Anime.original_anime_jp_name.ilike(f"%{anime_name}%")
            | Anime.anime_en_name.ilike(f"%{anime_name}%")
            | Anime.original_anime_en_name.ilike(f"%{anime_name}%")
        )

    # sorting
    # Check if the provided sort_by is a valid attribute of SiteGeneration
    if hasattr(Anime, sort_by) and not sort_by.startswith("_"):
        query = query.order_by(getattr(getattr(Anime, sort_by), order)())

    return query


@blueprint.route("/", methods=["GET", "POST"])
def anime_read():
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    query_args = get_query_args(request)

    form = AnimeSearchForm(**query_args)

    # if form is submitted, search anime in database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        form_data["page"] = 1

        try:
            return redirect(populate_url_with_args("/anime/", form_data))
        except Exception as e:
            return f"There was an issue performing the search: {e}"

    # get filtered anime from database
    query = db.session.query(Anime)
    query = filter_anime(query, **query_args)
    animes = query.all()

    # get total pages
    total_pages = len(animes) // query_args["page_size"] + 1

    # paginate anime
    animes = animes

    # deserizalize anime
    animes = [
        deserialize_anime(
            anime, extend_names=True, extend_genres=True, extend_tags=True
        )
        for anime in animes[
            (query_args["page"] - 1)
            * query_args["page_size"] : query_args["page"]
            * query_args["page_size"]
        ]
    ]

    for anime in animes:
        anime["anime_name"] = anime.pop("names")[0]["anime_name"]
        anime["anime_genres"] = ", ".join([genre for genre in anime.pop("genres", [])])
        anime["anime_tags"] = ", ".join([genre for genre in anime.pop("tags", [])])

    # render template w/ anime
    return render_template(
        "anime/read.jinja2",
        form=form,
        animes=animes,
        current_page=query_args["page"],
        total_pages=total_pages,
        username=session["username"],
    )


@blueprint.route("<int:ann_id>/", methods=["GET", "POST"])
def anime_update(ann_id):
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    # Initiliaze form with current anime data
    anime = Anime.query.get_or_404(ann_id)
    tags = ", ".join([tag.tag.tag for tag in anime.tags])
    genres = ", ".join([genre.genre.genre for genre in anime.genres])
    form = AnimeUpdateForm(obj=anime)

    # if form is submitted, add anime to database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        try:
            # validate args for model
            validate_sqla_object(Anime, form_data)
            # update anime in database
            db.session.query(Anime).filter_by(ann_id=ann_id).update({**form_data})
            db.session.commit()
            return redirect(f"/anime/{ann_id}")
        except ValueError as e:
            args = e.args[0]
            if "query" in args:
                for field, error in args["query"].items():
                    form[field].errors.extend(error)
            return render_template(
                "anime/update.jinja2",
                anime=anime,
                form=form,
                tags=tags,
                genres=genres,
                username=session["username"],
            )
        except Exception as e:
            return f"There was an issue editing your anime: {e}"

    # render template w/ animes
    return render_template(
        "anime/update.jinja2",
        anime=anime,
        form=form,
        tags=tags,
        genres=genres,
        username=session["username"],
    )
