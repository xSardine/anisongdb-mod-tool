# ORM
import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.songs.song import Song
from src.models.artists.line_up import LineUp, deserialize_line_up
from src.models.artists.artist import Artist, deserialize_artist
from src.models.artists.role_type import RoleType


# ----- Database ORM ----- #
class LinkSongArtist(BaseModel):
    __tablename__ = "Link_Song_Artist"

    id = sa.Column(sa.Integer, primary_key=True)

    id_song = sa.Column(sa.Integer, sa.ForeignKey(Song.id), nullable=False)
    song = relationship(Song, backref="artists")

    id_artist = sa.Column(sa.Integer, sa.ForeignKey(Artist.id), nullable=False)
    artist = relationship(Artist, backref="songs")

    id_artist_line_up = sa.Column(sa.Integer, sa.ForeignKey(LineUp.id), nullable=True)
    artist_line_up = relationship(LineUp, backref="songs")

    id_role_type = sa.Column(sa.Integer, sa.ForeignKey(RoleType.id), nullable=False)
    role_type = relationship(RoleType, backref="songs")

    __table_args__ = (
        UniqueConstraint(
            "id_song", "id_artist", "id_role_type", name="uq_link_song_artist"
        ),
    )


def deserialize_link_song_artist(
    link_song_artist,
    extend_artist: bool = False,
    extend_artist_line_up: bool = False,
    extend_role_type: bool = False,
):
    deserialized_link_song_artist = link_song_artist.as_dict()
    if extend_artist:
        deserialized_link_song_artist["artist"] = deserialize_artist(
            link_song_artist.artist, extend_names=True
        )

    if extend_artist_line_up and link_song_artist.artist_line_up is not None:
        deserialized_link_song_artist["artist_line_up"] = deserialize_line_up(
            link_song_artist.artist_line_up, extend_members=True
        )

    return deserialized_link_song_artist
