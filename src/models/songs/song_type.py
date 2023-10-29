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
class SongType(BaseModel):
    __tablename__ = "Song_Type"
    id = sa.Column(sa.Integer, primary_key=True)
    song_type = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_song_types_choices() -> List[Tuple]:
    """
    Function to retrieve all song_types from the database.

    Returns
    -------
    retrieve_song_types_choices : list of tuples
        List of tuples containing the song_type name and its ID.
    """

    retrieve_song_types_choices = SongType.query.all()

    choices = [
        (song_type.id, song_type.song_type) for song_type in retrieve_song_types_choices
    ]

    return choices
