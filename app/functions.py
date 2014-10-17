from subprocess import check_output, CalledProcessError
from app import sentry


def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def current_version():
    try:
        return check_output(['git', 'describe', '--always'])
    except CalledProcessError:
        sentry.captureException()
        return ""


def combine_dicts(a, b, path=None):
    """Totally stolen from http://stackoverflow.com/a/7205107/641710"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                combine_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
        else:
            a[key] = b[key]
    return a