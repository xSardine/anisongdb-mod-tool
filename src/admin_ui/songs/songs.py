# flask
from flask import Blueprint, render_template, redirect, session, request, jsonify
from flask import current_app as app

# models
from src.extensions import db
from src.models.songs.song import SongSearchForm, SongUpdateForm, Song
from src.models.songs.link_song_artist import deserialize_link_song_artist
from src.models.artists.role_type import RoleType

# authentification
from src.admin_ui.auth import authorized

# utils
from src.utils import validate_sqla_object
from src.admin_ui.utils import get_query_args, populate_url_with_args

# standard libraries
from pathlib import Path

# Typing helpers
from sqlalchemy.orm import Query

# ---- Admin UI Anime ---- #
blueprint = Blueprint("songs", __name__, url_prefix="/songs/")

CREDITS_FOLDER = Path("src/static/images/credits")
CREDITS_FOLDER.mkdir(parents=True, exist_ok=True)
CREDIS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]


def filter_songs(
    query: Query,
    song_name: str = None,
    artist_name: str = None,
    sort_by: str = "id",
    order: str = "asc",
    **unfilteredArgs: any,
) -> Query:
    """
    Filter a query on songs depending on query args filters. It include filters from different tables.

    Parameters
    ----------
    query : SQLAlchemy query
        The query to filter
    song_name : str
        The name of the song to filter on
    artist_name : str
        The name of the artist to filter on
    **unfilteredArgs : any
        Other args that are not used for filtering

    Returns
    -------
    SQLAlchemy query
        The filtered query
    """

    # filter on song_name and original_song_name, not case sensitive

    if song_name:
        query = query.filter(
            Song.song_name.ilike(f"%{song_name}%")
            | Song.original_song_name.ilike(f"%{song_name}%")
        )

    if artist_name:
        query = query.filter(
            Song.song_artist.ilike(f"%{artist_name}%")
            | Song.original_song_artist.ilike(f"%{artist_name}%")
        )

    # sorting
    # Check if the provided sort_by is a valid attribute of SiteGeneration
    if hasattr(Song, sort_by) and not sort_by.startswith("_"):
        query = query.order_by(getattr(getattr(Song, sort_by), order)())

    return query


@blueprint.route("/", methods=["GET", "POST"])
def songs_read():
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    query_args = get_query_args(request)

    form = SongSearchForm(**query_args)

    # if form is submitted, search song in database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        form_data["page"] = 1

        try:
            return redirect(populate_url_with_args("/songs/", form_data))
        except Exception as e:
            return f"There was an issue performing the search: {e}"

    else:
        print("form not validated : ", form.errors)

    # get filtered songs from database
    query = db.session.query(Song)
    query = filter_songs(query, **query_args)
    songs = query.all()

    # get total pages
    total_pages = len(songs) // query_args["page_size"] + 1

    # paginate songs
    songs = songs[
        (query_args["page"] - 1)
        * query_args["page_size"] : query_args["page"]
        * query_args["page_size"]
    ]

    # deserizalize songs
    songs = [song.as_dict() for song in songs]

    # render template w/ songs
    return render_template(
        "songs/read.jinja2",
        form=form,
        songs=songs,
        current_page=query_args["page"],
        total_pages=total_pages,
        username=session["username"],
    )


def find_song_credits(id_song: int) -> Path:
    # Function to find the credits file based on existing file extensions and song_id
    for extension in CREDIS_ALLOWED_EXTENSIONS:
        credits_path = CREDITS_FOLDER / f"{id_song}{extension}"
        if credits_path.exists():
            return credits_path

    return None


@blueprint.route("<int:id_song>/", methods=["GET", "POST"])
def song_update(id_song):
    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    song = Song.query.get_or_404(id_song)

    song_artists = {}
    for role_type in RoleType.query.all():
        song_artists[role_type.role_type] = [
            link_song_artist
            for link_song_artist in song.artists
            if link_song_artist.role_type.role_type == role_type.role_type
        ]

    # Initiliaze form with current song data
    form = SongUpdateForm(obj=song)

    credits_path = find_song_credits(id_song)
    credits_relative_path = credits_path.relative_to("src") if credits_path else None

    # if form is submitted, add song to database
    if form.validate_on_submit():
        # retrieve form data excluding csrf_token
        form_data = {
            key: value or None
            for key, value in form.data.items()
            if key != "csrf_token"
        }

        try:
            # validate args for model
            validate_sqla_object(Song, form_data)

            # update song in database
            db.session.query(Song).filter_by(id=id_song).update({**form_data})
            song = (song,)
            db.session.commit()
            return redirect(f"/songs/{id_song}")
        except ValueError as e:
            args = e.args[0]
            if "query" in args:
                for field, error in args["query"].items():
                    form[field].errors.extend(error)
            return render_template(
                "songs/update.jinja2",
                form=form,
                song_artists=song_artists,
                username=session["username"],
                credits_path=credits_relative_path,
            )
        except Exception as e:
            return f"There was an issue editing your song: {e}"

    # render template w/ songs
    return render_template(
        "songs/update.jinja2",
        form=form,
        song_artists=song_artists,
        username=session["username"],
        credits_path=credits_relative_path,
    )


@blueprint.route("<int:id_song>/upload/", methods=["POST"])
def song_credits_upload(id_song):
    # Check if the POST request has a file part
    if "file" not in request.files:
        print("no file found")
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    # check that the file could be loaded
    if not file:
        print("no file selected")
        return jsonify({"error": "No file selected"}), 400

    current_file = CREDITS_FOLDER / Path(file.filename)

    # Check if the file is present and has an allowed extension
    if current_file.suffix in CREDIS_ALLOWED_EXTENSIONS:
        # check if there is already an image for this song
        current_credit_path = find_song_credits(id_song)
        # if there is one, delete it
        if current_credit_path:
            current_credit_path.unlink()

        # rename the file to the song id
        output_file = CREDITS_FOLDER / Path(f"{id_song}{current_file.suffix}")

        # Save the file
        file.save(output_file)

        return jsonify({"success": True}), 200
    else:
        print("invalid file format")
        return jsonify({"error": "Invalid file format"}), 400
