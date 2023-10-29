# ORM
import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.anime.anime import Anime
from src.models.anime.genre import Genre


class LinkAnimeGenre(BaseModel):
    __tablename__ = "Link_Anime_Genre"

    id_anime = sa.Column(sa.Integer, sa.ForeignKey(Anime.id), nullable=False)
    anime = relationship(Anime, backref="genres")

    id_genre = sa.Column(sa.Integer, sa.ForeignKey(Genre.id), nullable=False)
    genre = relationship(Genre, backref="animes")

    # Define a composite primary key
    __table_args__ = (PrimaryKeyConstraint("id_anime", "id_genre"),)
