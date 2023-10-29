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
class AnimeNameType(BaseModel):
    __tablename__ = "Anime_Name_Type"
    id = sa.Column(sa.Integer, primary_key=True)
    anime_name_type = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_anime_name_type_choices() -> List[Tuple]:
    """
    Function to retrieve all anime_name_type from the database.

    Returns
    -------
    retrieve_anime_name_type_choices : list of tuples
        List of tuples containing the anime_name_type name and its ID.
    """

    retrieve_anime_name_type_choices = AnimeNameType.query.all()

    choices = [
        (anime_name_type.id, anime_name_type.anime_name_type)
        for anime_name_type in retrieve_anime_name_type_choices
    ]

    return choices
