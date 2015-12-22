import urlparse
from app import steam, db
from steam.user import VanityError, ProfileNotFoundError
from steam.api import HTTPError, HTTPTimeoutError
from ..models import get_or_create
from ..users.models import User


def get_steam_id_from_url(profile_url):
    parsed_url = urlparse.urlparse(profile_url)
    split_path = parsed_url.path[1:].split('/')
    if parsed_url.hostname == "steamcommunity.com":
        if "id" in split_path[0]:
            try:
                return True, steam.user.vanity_url(profile_url).id64
            except (ProfileNotFoundError, VanityError):
                return False, "User not found."
            except (HTTPError, HTTPTimeoutError):
                return False, "Steam error. Please try again later."
        elif "profiles" in split_path[0]:
            return True, split_path[1]
    else:
        return False, "Please insert a valid Steam profile URL."


def new_user(profile_url):

    steam_id_info = get_steam_id_from_url(profile_url)

    if steam_id_info[0] is True:
        steam_id = long(steam_id_info[1])
        account_id = int(steam_id & 0xFFFFFFFF)
        author = get_or_create(db.session, User, account_id=account_id,
                               create_args={'signed_in': False, 'last_seen': 0})
        db.session.add(author)
        db.session.commit()
        return author
    else:
        return steam_id_info[1]