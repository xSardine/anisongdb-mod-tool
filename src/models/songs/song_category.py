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
class SongCategory(BaseModel):
    __tablename__ = "Song_Category"
    id = sa.Column(sa.Integer, primary_key=True)
    song_category = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_song_categories_choices() -> List[Tuple]:
    """
    Function to retrieve all song_categorys from the database.

    Returns
    -------
    retrieve_song_categories_choices : list of tuples
        List of tuples containing the song_category name and its ID.
    """

    retrieve_song_categories_choices = SongCategory.query.all()

    choices = [
        (song_category.id, song_category.song_category)
        for song_category in retrieve_song_categories_choices
    ]

    return choices
