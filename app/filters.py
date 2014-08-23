from flask import current_app
from datetime import datetime
def format_thousands(number):
    return "{:,}".format(number)


def pluralize(number, singular='', plural='s'):
    if number == 1:
        return singular
    else:
        return plural


def datetime_to_datestring(_input, _format=None):
    """ Take a datetime object and output it in the format specified in the site's config. """
    _format = _format or current_app.config["DATE_STRING_FORMAT"]
    if isinstance(_input, datetime):
        return _input.strftime(_format)
    else:
        return None