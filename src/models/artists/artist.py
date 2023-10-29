# ORM
import sqlalchemy as sa
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.artists.artist_type import ArtistType, retrieve_artist_type_choices

# Forms
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm
from wtforms.fields import SelectField, StringField, IntegerField
from wtforms.validators import InputRequired


class Artist(BaseModel):
    __tablename__ = "Artist"

    id = sa.Column(sa.Integer, primary_key=True)

    id_artist_type = sa.Column(sa.Integer, sa.ForeignKey(ArtistType.id), nullable=False)
    artist_type = relationship(ArtistType)

    artist_disambiguation = sa.Column(sa.String(200), nullable=True)

    # ----- Validators ----- #
    @validates("artist_name")
    def validate_territoire_coordination(self, key, value):
        if len(value) < 0:
            raise ValueError(
                {
                    "query": {
                        key: [
                            f"{key} must be at least 0 characters long. {value} is not a valid value for {key}"
                        ]
                    }
                }
            )
        return value


# ModelForm to imitate the ORM model & FlaskForm to use the automatic CRSF protection
class ArtistUpdateForm(ModelForm, FlaskForm):
    """
    Class defining :
    - the form fields for creation of a new "artist" object.
    - the form fields for update of an existing "artist" object.
    """

    id_artist_type = SelectField(
        label="Artist Type",
        choices=[],
        validators=[InputRequired()],
    )

    class Meta:
        model = Artist
        exclude = []
        include = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_artist_type.choices = retrieve_artist_type_choices()


class ArtistSearchForm(FlaskForm):
    artist_name = StringField("Artist Name")
    page = IntegerField(label="Page", default=1)
    page_size = IntegerField(label="Page size", default=50)


def deserialize_artist(
    artist: Artist, extend_names: bool = False, extend_songs: bool = False
):
    deserialized_artist = artist.as_dict()
    if extend_names:
        deserialized_artist["names"] = [
            {
                "artist_name": name.artist_name,
                "original_artist_name": name.original_artist_name,
            }
            for name in artist.artist_names
        ]

    return deserialized_artist
