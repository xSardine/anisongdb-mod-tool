from flask import abort

# orm
from sqlalchemy import inspect

# Type hinting helpers
from sqlalchemy.orm import DeclarativeBase


def validate_sqla_object(model: DeclarativeBase, args: dict = {}):
    """
    Validate that args are valid for a sqla object.

    Parameters
    ----------
    model : DeclarativeBase
        The sqla model to validate against.
    args : dict
        The args to validate, ignore any args that isn't an attribute of SiteGeneration

    Raises
    ------
    ma.ValidationError
        If args are not valid for this model
    """

    # extract model keys
    mapper = inspect(model)
    model_keys = [column.key for column in mapper.attrs]

    # only keep args that are in model keys
    validator_args = {arg: args[arg] for arg in args if arg in model_keys}

    # validate that args are valid
    try:
        model(**validator_args)
    except ValueError as e:
        raise e
    except Exception as e:
        abort(e)
