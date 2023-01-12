"""Utility functions of the collectivo app."""
import os


def string_to_list(string: str):
    """Convert a string with items seperated by comma to a list."""
    if string == '' or string is None:
        return []
    else:
        return string.replace(' ', '').split(',')


def get_env_bool(key, default=None):
    """Take the name of an environment variable and return a boolean."""
    options = {
        'false': False,
        'False': False,
        0: False,
        '0': False,
        'true': True,
        'True': True,
        '1': True,
        1: True,
    }
    value = os.environ.get(key, default)
    if isinstance(value, bool):
        return value
    elif value in options:
        return options[value]
    else:
        raise AttributeError(
            f"Environment variable {key} must be 'true' or 'false'."
        )
