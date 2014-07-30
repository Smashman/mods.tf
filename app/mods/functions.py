from flask import abort
from flask.ext.login import current_user


def check_mod_permissions(mod):
    if mod.completed is False or mod.enabled is False:
        abort(404)
    elif mod.visibility != "Pu" and current_user not in mod.authors and not current_user.is_admin():
        abort(403)


def check_edit_permissions(mod):
    check_mod_permissions(mod)
    if current_user not in mod.authors and not current_user.is_admin():
        abort(403)