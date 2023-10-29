# ORM
import sqlalchemy as sa
from src.models.extensions import BaseModel


# ----- Database ORM ----- #
class Tag(BaseModel):
    __tablename__ = "Tag"
    id = sa.Column(sa.Integer, primary_key=True)
    tag = sa.Column(sa.String, nullable=False, unique=True)
