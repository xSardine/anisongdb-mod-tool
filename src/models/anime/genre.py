# ORM
import sqlalchemy as sa
from src.models.extensions import BaseModel


# ----- Database ORM ----- #
class Genre(BaseModel):
    __tablename__ = "Genre"
    id = sa.Column(sa.Integer, primary_key=True)
    genre = sa.Column(sa.String, nullable=False, unique=True)
