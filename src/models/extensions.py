"""Models extension initialization.

Override base classes here to allow painless customization in the future.

Inspired by https://github.com/lafrech/flask-smorest-sqlalchemy-example/blob/master/team_manager/extensions/api/__init__.py
"""

# marshmallow schema override to automatically include update method with SQLAlchemyAutoSchema
import json
from sqlalchemy import inspect

# ORM
from src.extensions import db


class BaseModel(db.Model):
    """Extend SQLAlchemy base db.model with as_dict and as_json methods"""

    __abstract__ = True

    def as_dict(self):
        # Get the columns of the current class
        current_columns = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        # Get the columns of the inherited class if there is one
        inherited_columns = {
            c.key: getattr(self, c.key)
            for c in inspect(self.__class__).mapper.column_attrs
        }

        # Combine both dictionaries
        output_dict = {**current_columns, **inherited_columns}

        return output_dict

    def as_json(self):
        return json.dumps(self.as_dict())
