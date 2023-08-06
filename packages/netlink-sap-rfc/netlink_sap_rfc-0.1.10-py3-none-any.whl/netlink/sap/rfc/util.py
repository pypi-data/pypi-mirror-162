import datetime
from netlink.logging import logger

from .exception import BapiException


def dats_to_date(dats: str):
    try:
        return datetime.datetime.strptime(dats, '%Y%m%d').date()
    except ValueError:
        return None


def tims_to_time(tims: str):
    try:
        return datetime.datetime.strptime(tims, '%H%M%S').time()
    except ValueError:
        return None


def datstims_to_datetime(dats: str, tims: str):
    try:
        return datetime.datetime.strptime(f'{dats}{tims}', '%Y%m%d%H%M%S')
    except ValueError:
        return None


def format_bapi_return(value):
    return {"S": logger.SUCCESS,
            "I": logger.INFO,
            "W": logger.WARNING,
            "E": logger.ERROR,
            "A": logger.CRITICAL}.get(value.type, logger.VERBOSE), f"{value.id}-{value.number}: {value.message}"


def bapi_return(value):
    """Log any contents of BAPIRET2 depending on log level. Returning Exception if 'E' or 'A'."""
    if not isinstance(value, list):
        value = [value,]
    result = []
    messages = []
    for i in value:
        if i.type in ('E', 'A'):
            result.append(BapiException(i, messages))
        messages.append(i)
        logger.log(*format_bapi_return(i))
    return result
