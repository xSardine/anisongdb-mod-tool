from flask import Blueprint, redirect, session, send_from_directory
from flask import current_app as app

blueprint = Blueprint("/", __name__)


@blueprint.route("/", methods=["GET", "POST"])
def index():
    session["username"] = "admin"

    # if not authorized, redirect to login page
    if "username" not in session:
        return redirect("/auth")

    return redirect("/artists")


# Example usage
@blueprint.route("/static/<path:filename>")
def static_file(filename):
    response = send_from_directory("static", filename)
    # Set cache-control header for static files
    response.headers[
        "Cache-Control"
    ] = "public, max-age=1209600"  # Cache for 2 weeks (in seconds)

    return response
