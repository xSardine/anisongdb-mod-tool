# flake8: noqa:F401
# env
import os
from dotenv import dotenv_values

# flask
from flask import Flask, render_template, request, abort

# blueprints
from src import admin_ui
from src import routes

# extensions
from src.extensions import cache, csrf_protect, db, override_url_for


def create_app():
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_folder=None)

    register_config(app)
    register_extensions(app)
    register_blueprint(app)
    # register_errorhandlers(app)
    return app


def register_config(app):
    """Register configuration variables."""

    # Authorize HTTP requests
    # TODO: DON'T DO THIS IN PRODUCTION!
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # fix scope issue https://github.com/requests/requests-oauthlib/issues/387
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    config = {
        **dotenv_values(".env.shared"),  # load shared development variables
        **dotenv_values(".env.secret"),  # load sensitive variables
        **os.environ,  # override loaded values with environment variables
    }

    config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f'postgresql://{config["POSTGRES_USER"]}:{config["POSTGRES_PASSWORD"]}@{config["POSTGRES_HOST"]}:{config["POSTGRES_PORT"]}/{config["POSTGRES_DB"]}'
    print(config["SQLALCHEMY_DATABASE_URI"])

    # Add config
    app.config.from_mapping(config)

    # Set up test accounts TODO
    app.config["AUTHORIZED_USERS"] = app.config["AUTHORIZED_USERS"].split(",")

    # Set up cache
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = config["APP_SESSION_SECRET_KEY"]

    return None


def register_extensions(app):
    # override url_for to allow cache busting
    app.context_processor(override_url_for)

    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # TODO: break api POST/DELETE/PUT request ??
    # csrf_protect.init_app(app)
    return None


def register_blueprint(app):
    """Register Flask blueprints."""
    app.register_blueprint(admin_ui.anime.blueprint)
    app.register_blueprint(admin_ui.link_anime_name.blueprint)
    app.register_blueprint(admin_ui.songs.blueprint)
    app.register_blueprint(admin_ui.link_song_artist.blueprint)
    app.register_blueprint(admin_ui.artists.blueprint)
    app.register_blueprint(admin_ui.link_artist_name.blueprint)
    app.register_blueprint(admin_ui.link_artist_line_up.blueprint)
    app.register_blueprint(admin_ui.auth.blueprint)
    app.register_blueprint(routes.blueprint)
    app.register_blueprint(admin_ui.autocomplete.blueprint)

    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        # If the request is not from the API, render the error template
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.jinja2"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)

    return None
