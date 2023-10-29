# ORM
import sqlalchemy as sa
from sqlalchemy.orm import validates
from src.models.extensions import BaseModel

# Forms
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm

# typing helpers
from typing import List, Tuple


# ----- Database ORM ----- #
class ArtistType(BaseModel):
    __tablename__ = "Artist_Type"
    id = sa.Column(sa.Integer, primary_key=True)
    artist_type = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_artist_type_choices() -> List[Tuple]:
    """
    Function to retrieve all artist_type from the database.

    Returns
    -------
    retrieve_artist_type_choices : list of tuples
        List of tuples containing the artist_type name and its ID.
    """

    retrieve_artist_type_choices = ArtistType.query.all()

    choices = [
        (artist_type.id, artist_type.artist_type)
        for artist_type in retrieve_artist_type_choices
    ]

    return choices
