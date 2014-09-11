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