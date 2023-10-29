# ORM
import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.anime.anime import Anime
from src.models.anime.tag import Tag


class LinkAnimeTag(BaseModel):
    __tablename__ = "Link_Anime_Tag"

    id_anime = sa.Column(sa.Integer, sa.ForeignKey(Anime.id), nullable=False)
    anime = relationship(Anime, backref="tags")

    id_tag = sa.Column(sa.Integer, sa.ForeignKey(Tag.id), nullable=False)
    tag = relationship(Tag, backref="animes")

    # Define a composite primary key
    __table_args__ = (PrimaryKeyConstraint("id_anime", "id_tag"),)
