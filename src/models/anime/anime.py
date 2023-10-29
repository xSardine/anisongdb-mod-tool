# ORM
import sqlalchemy as sa
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.anime.anime_type import AnimeType, retrieve_anime_type_choices

# Forms
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm
from wtforms.fields import SelectField, StringField, IntegerField
from wtforms.validators import InputRequired

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import InputRequired, Length


class Anime(BaseModel):
    __tablename__ = "Anime"

    id = sa.Column(sa.Integer, primary_key=True)

    ann_id = sa.Column(sa.Integer, nullable=False, unique=True)

    id_anime_type = sa.Column(sa.Integer, sa.ForeignKey(AnimeType.id), nullable=True)
    anime_type = relationship(AnimeType)

    anime_vintage = sa.Column(sa.String(200), nullable=True)


# ModelForm to imitate the ORM model & FlaskForm to use the automatic CRSF protection
class AnimeUpdateForm(ModelForm, FlaskForm):
    """
    Class defining :
    - the form fields for creation of a new "anime" object.
    - the form fields for update of an existing "anime" object.
    """

    id_anime_type = SelectField(
        label="Anime Type",
        choices=[],
        validators=[InputRequired()],
    )

    class Meta:
        model = Anime
        exclude = []
        include = ["id_anime_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_anime_type.choices = retrieve_anime_type_choices()


class AnimeSearchForm(FlaskForm):
    anime_name = StringField("Anime Name")
    page = IntegerField(label="Page", default=1)
    page_size = IntegerField(label="Page size", default=50)


def deserialize_anime(
    anime,
    extend_names: bool = False,
    extend_genres: bool = False,
    extend_tags: bool = False,
):
    deserialized_anime = anime.as_dict()

    deserialized_anime["anime_type"] = (
        anime.anime_type.anime_type if anime.anime_type else None
    )

    if extend_names:
        deserialized_anime["names"] = []
        for name in anime.names:
            deserialized_anime["names"].append(
                {
                    "anime_name_type": name.anime_name_type.anime_name_type,
                    "anime_name": name.anime_name,
                    "original_anime_name": name.original_anime_name,
                }
            )

    if extend_genres and anime.genres:
        deserialized_anime["genres"] = []
        for genre in anime.genres:
            deserialized_anime["genres"].append(genre.genre.genre)

    if extend_tags and anime.tags:
        deserialized_anime["tags"] = []
        for tag in anime.tags:
            deserialized_anime["tags"].append(tag.tag.tag)

    return deserialized_anime
