# ORM
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.artists.line_up import LineUp
from src.models.artists.artist import Artist
from src.models.artists.role_type import RoleType


# ----- Database ORM ----- #
class LinkArtistLineUp(BaseModel):
    __tablename__ = "Link_Artist_Line_Up"

    id = sa.Column(sa.Integer, primary_key=True)

    id_member = sa.Column(sa.Integer, sa.ForeignKey(Artist.id), nullable=False)
    member = relationship(Artist, foreign_keys=[id_member], backref="groups")

    id_member_line_up = sa.Column(sa.Integer, sa.ForeignKey(LineUp.id), nullable=True)
    member_line_up = relationship(LineUp, foreign_keys=[id_member_line_up])

    id_role_type = sa.Column(sa.Integer, sa.ForeignKey(RoleType.id), nullable=False)
    role_type = relationship(RoleType, foreign_keys=[id_role_type])

    id_group = sa.Column(sa.Integer, sa.ForeignKey(Artist.id), nullable=False)
    group = relationship(Artist, foreign_keys=[id_group])

    id_group_line_up = sa.Column(sa.Integer, sa.ForeignKey(LineUp.id), nullable=False)
    group_line_up = relationship(
        LineUp, foreign_keys=[id_group_line_up], backref="members"
    )

    __table_args__ = (
        UniqueConstraint(
            "id_member",
            "id_role_type",
            "id_group",
            "id_group_line_up",
            name="uq_link_artist_line_up",
        ),
    )
