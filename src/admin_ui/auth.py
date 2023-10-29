"""Blueprint & functions for Admin UI authentification & authorization.
"""

from flask import Blueprint, redirect, session, render_template, request
from flask import current_app as app

from flask_wtf import FlaskForm
from wtforms import StringField


# TODO temporary guest form
class GuestForm(FlaskForm):
    username = StringField("Username")
    password = StringField("Password")


def authorized(f):
    """
    Decorator to check if user is authenticated and authorized to access the page

    A user is authenticated if cerbere has authorized him.
    TODO: right now it is not implemented and everyone is authorized as long as they are logged in a session
    """

    def decorator(*args, **kwargs):
        # TODO check if user is authorized via cerbere when cerbere is implemented
        if "username" not in session:
            return redirect("/auth")
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator


# ---- Admin UI Authentification Blueprint ---- #
blueprint = Blueprint("auth", __name__)


@blueprint.route("/auth/", methods=["GET", "POST"])
def auth():
    # temporary login method for guests accounts
    form = GuestForm()
    if form.validate_on_submit():
        usernames = app.config["GUEST_USER_NAMES"].split(",")
        passwords = app.config["GUEST_USER_PASSWORDS"].split(",")
        for username, pwd in zip(usernames, passwords):
            if form.username.data == username and form.password.data == pwd:
                session["username"] = username
                session["api_key"] = "TODO"
                return redirect("/")

    elif form.errors:
        print(f"form not validated on submit because : {form.errors}")

    # if already authorized via google or cerbere, enter app
    if "username" in session:
        return redirect("/")

    # if not authorized, show login page
    return render_template("auth.jinja2", form=form)


# logout
@blueprint.route("/auth/logout/")
def logout():
    # TODO: revoke token
    session.pop("username", None)  # delete username from session
    session.pop("api_key", None)  # delete api_key from session
    return redirect("/auth")
