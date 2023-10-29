# ORM
import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import validates, relationship, backref

# Extensions
from src.models.extensions import BaseModel

# Related models
from src.models.artists.artist import Artist, deserialize_artist


# ----- Database ORM ----- #
class LineUp(BaseModel):
    __tablename__ = "Line_Up"

    id = sa.Column(sa.Integer, primary_key=True)

    id_artist = sa.Column(sa.Integer, sa.ForeignKey(Artist.id), nullable=False)
    artist = relationship(Artist, backref="line_ups")


def deserialize_line_up(line_up, extend_members: bool = False):
    deserialized_line_up = line_up.as_dict()

    deserialized_line_up["names"] = deserialize_artist(
        line_up.artist, extend_names=True
    )["names"]

    if extend_members:
        members = []
        for member in line_up.members:
            if member.id_member_line_up is not None:
                members.append(
                    deserialize_line_up(member.member_line_up, extend_members=True)
                )
            else:
                members.append(deserialize_artist(member.member, extend_names=True))
        deserialized_line_up["members"] = members

    return deserialized_line_up
