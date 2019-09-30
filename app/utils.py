import decimal
import enum
import string
from datetime import datetime

from random import choice, randint

from bson.objectid import ObjectId
from flask import g


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def get_current_user():
    return getattr(g, 'user', None)


def generate_random_code(n=6):
    return ''.join([str(randint(0, 9)) for i in range(n)])


def generate_random_string(n=20):
    return ''.join([choice(string.ascii_lowercase) for i in range(n)])


def get_model_value(val):
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, ObjectId):
        return str(val)
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, enum.Enum):
        return val.value
    if isinstance(val, bytes):
        return str(val, 'utf-8')
    return val


def to_json(val, fields=None):
    keys = val.keys()
    if fields is None:
        res = {
            k: get_model_value(val[k]) for k in keys
        }
    return res
