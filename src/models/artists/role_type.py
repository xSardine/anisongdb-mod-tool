# ORM
import sqlalchemy as sa
from sqlalchemy.orm import validates
from src.models.extensions import BaseModel

# Forms
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm

# typing helpers
from typing import List, Tuple


# ----- Database ORM ----- #
class RoleType(BaseModel):
    __tablename__ = "Role_Type"
    id = sa.Column(sa.Integer, primary_key=True)
    role_type = sa.Column(sa.String, nullable=False, unique=True)


def retrieve_role_type_choices() -> List[Tuple]:
    """
    Function to retrieve all role_type from the database.

    Returns
    -------
    retrieve_role_type_choices : list of tuples
        List of tuples containing the role_type name and its ID.
    """

    retrieve_role_type_choices = RoleType.query.all()

    choices = [
        (role_type.id, role_type.role_type) for role_type in retrieve_role_type_choices
    ]

    return choices
