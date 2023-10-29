# ORM
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.songs.song_type import SongType, retrieve_song_types_choices
from src.models.songs.song_category import (
    SongCategory,
    retrieve_song_categories_choices,
)
from src.models.anime.anime import Anime

# Forms
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm
from wtforms.fields import SelectField, StringField, IntegerField
from wtforms.validators import InputRequired


class Song(BaseModel):
    __tablename__ = "Song"

    id = sa.Column(sa.Integer, primary_key=True)

    id_anime = sa.Column(sa.Integer, sa.ForeignKey(Anime.id), nullable=False)
    anime = relationship(Anime, backref="songs")

    id_song_type = sa.Column(sa.Integer, sa.ForeignKey(SongType.id), nullable=False)
    song_type = relationship(SongType)

    song_number = sa.Column(sa.Integer, nullable=True)

    song_name = sa.Column(sa.String, nullable=False)
    original_song_name = sa.Column(sa.String, nullable=True)

    song_artist = sa.Column(sa.String, nullable=False)
    original_song_artist = sa.Column(sa.String, nullable=True)

    song_composer = sa.Column(sa.String, nullable=True)
    original_song_composer = sa.Column(sa.String, nullable=True)

    song_arranger = sa.Column(sa.String, nullable=True)
    original_song_arranger = sa.Column(sa.String, nullable=True)

    id_song_category = sa.Column(
        sa.Integer, sa.ForeignKey(SongCategory.id), nullable=True
    )
    song_category = relationship(SongCategory)

    song_difficulty = sa.Column(sa.String, nullable=True)

    HQ = sa.Column(sa.String, nullable=True)
    MQ = sa.Column(sa.String, nullable=True)
    audio = sa.Column(sa.String, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "id_anime",
            "id_song_type",
            "song_number",
            "song_name",
            "song_artist",
            name="uq_song",
        ),
    )


# ModelForm to imitate the ORM model & FlaskForm to use the automatic CRSF protection
class SongUpdateForm(ModelForm, FlaskForm):
    """
    Class defining :
    - the form fields for creation of a new "artist" object.
    - the form fields for update of an existing "artist" object.
    """

    id_song_type = SelectField(
        label="Artist Type",
        choices=[],
        validators=[InputRequired()],
    )

    id_song_category = SelectField(
        label="Artist Type",
        choices=[],
        validators=[InputRequired()],
    )

    class Meta:
        model = Song
        exclude = []
        include = ["id_song_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_song_type.choices = retrieve_song_types_choices()
        self.id_song_category.choices = retrieve_song_categories_choices()


class SongSearchForm(FlaskForm):
    song_name = StringField("Song Name")
    artist_name = StringField("Artist Name")
    page = IntegerField(label="Page", default=1)
    page_size = IntegerField(label="Page size", default=50)
