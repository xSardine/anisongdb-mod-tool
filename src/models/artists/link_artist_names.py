# ORM
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.artists.artist import Artist


class LinkArtistName(BaseModel):
    __tablename__ = "Link_Artist_Name"

    id = sa.Column(sa.Integer, primary_key=True)

    id_artist = sa.Column(sa.Integer, sa.ForeignKey(Artist.id), nullable=False)
    artist = relationship(Artist, backref="artist_names")

    artist_name = sa.Column(sa.String, nullable=False)
    original_artist_name = sa.Column(sa.String)

    order = sa.Column(sa.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id_artist",
            "artist_name",
            "original_artist_name",
            name="uq_link_artist_name",
        ),
    )
