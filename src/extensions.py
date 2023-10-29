# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in src/__init__.py."""
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

from flask import current_app as app

import random, string

csrf_protect = CSRFProtect()
db = SQLAlchemy()
cache = Cache(config={"CACHE_TYPE": "simple"})


def override_url_for():
    """
    Override Flask's `url_for` function to append a unique query parameter
    (timestamp) to the URL of the static file.
    This allow to force the browser to reload the static files when they have been modified.
    Needs APP_VERSION to be set in the config.
    """

    def dated_url_for(endpoint, **values):
        if endpoint == "/.static_file":
            filename = values.get("filename", None)
            if filename:
                # if the app is in debug mode, use a random string to force the browser to reload the static files
                if app.debug:
                    values["v"] = "".join(
                        random.choice(string.ascii_letters) for i in range(10)
                    )
                # else, use the APP_VERSION from the config
                else:
                    values["v"] = app.config["APP_VERSION"]

        return url_for(endpoint, **values)

    return dict(url_for=dated_url_for)
