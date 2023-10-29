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
class AnimeType(BaseModel):
    __tablename__ = "Anime_Type"
    id = sa.Column(sa.Integer, primary_key=True)
    anime_type = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_anime_type_choices() -> List[Tuple]:
    """
    Function to retrieve all anime_type from the database.

    Returns
    -------
    retrieve_anime_type_choices : list of tuples
        List of tuples containing the anime_type name and its ID.
    """

    retrieve_anime_type_choices = AnimeType.query.all()

    choices = [
        (anime_type.id, anime_type.anime_type)
        for anime_type in retrieve_anime_type_choices
    ]

    return choices
