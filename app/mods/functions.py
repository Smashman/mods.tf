import urlparse
import os
from flask import abort
from app import steam, db
from flask.ext.login import current_user
from app.models import get_or_create
from app.users.models import User
from steam.user import VanityError, ProfileNotFoundError


def check_mod_permissions(mod):
    if mod.completed is False or mod.enabled is False:
        abort(404)
    elif mod.visibility != "Pu" and current_user not in mod.authors and not current_user.is_admin():
        abort(403)


def check_edit_permissions(mod):
    check_mod_permissions(mod)
    if current_user not in mod.authors and not current_user.is_admin():
        abort(403)


def new_author(profile_url):
    parsed_url = urlparse.urlparse(profile_url)
    steam_id = None
    split_path = os.path.split(os.path.normpath(parsed_url.path))
    print split_path
    if parsed_url.hostname == "steamcommunity.com":
        if "id" in split_path[0]:
            try:
                steam_id = steam.user.vanity_url(profile_url).id64
            except (ProfileNotFoundError, VanityError):
                return "User not found."
        elif "profiles" in split_path[0]:
            steam_id = split_path[1]

    if steam_id:
        steam_id = long(steam_id)
        account_id = int(steam_id & 0xFFFFFFFF)
        author = get_or_create(db.session, User, account_id=account_id,
                               create_args={'signed_in': False, 'last_seen': 0})
        db.session.add(author)
        db.session.commit()
        return author
    else:
        return "Please insert a valid Steam profile URL."