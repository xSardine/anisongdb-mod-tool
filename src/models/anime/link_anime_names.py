# ORM
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.anime.anime import Anime
from src.models.anime.anime_name_type import AnimeNameType


class LinkAnimeName(BaseModel):
    __tablename__ = "Link_Anime_Name"

    id = sa.Column(sa.Integer, primary_key=True)

    id_anime = sa.Column(sa.Integer, sa.ForeignKey(Anime.id), nullable=False)
    anime = relationship(Anime, backref="names")

    id_anime_name_type = sa.Column(
        sa.Integer, sa.ForeignKey(AnimeNameType.id), nullable=False
    )
    anime_name_type = relationship(AnimeNameType)

    anime_name = sa.Column(sa.String, nullable=False)
    original_anime_name = sa.Column(sa.String)

    __table_args__ = (
        UniqueConstraint(
            "id_anime",
            "id_anime_name_type",
            "anime_name",
            name="uq_link_anime_name",
        ),
    )
