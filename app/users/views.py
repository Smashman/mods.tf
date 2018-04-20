from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app, g
from app import oid, db, login_manager
from models import User, AnonymousUser
from flask.ext.login import login_user, logout_user, current_user, login_required
from ..mods.models import Mod
from sqlalchemy.exc import IntegrityError

users = Blueprint("users", __name__, url_prefix="/users")

login_manager.anonymous_user = AnonymousUser


# User authentication
@login_manager.user_loader
def load_user(user_id):
    _user = User.query.get(user_id)
    if _user:
        _user.update_last_seen()
    if _user and _user.enabled is False:
        logout_user()
        flash("You have been banned from using this website.", "danger")
        redirect(url_for("index"))
    return _user


@users.route('/login/')
@oid.loginhandler
def login():
    if current_user.is_authenticated():
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')


@oid.after_login
def create_or_login(resp):
    steam_id = long(resp.identity_url.replace("https://steamcommunity.com/openid/id/", ""))
    account_id = int(steam_id & 0xFFFFFFFF)
    _user = User.query.get(account_id)
    new_user = False

    if not _user:
        _user = User(account_id)
        new_user = True
        db.session.add(_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            _user = User.query.get(account_id)

    if not _user.signed_in:
        _user.signed_in = True
        db.session.add(_user)
        db.session.commit()

    if not _user.is_active():
        flash(u"Cannot log you in, {}. You are banned.".format(_user.name), "danger")
        return redirect(oid.get_next_url())

    login_attempt = login_user(_user, remember=True)
    if login_attempt is True and new_user and _user.profile_url:
        flash(u"Welcome to mods.tf, {}!".format(_user.name), "success")
    elif login_attempt is True and new_user and not _user.profile_url:
        flash(u"Welcome to mods.tf! Unfortunately were unable to fetch your Steam user data."
              u"We will try again soon. For now you will be represented by your numerical ID, {}.".format(_user.name), "success")
    elif login_attempt is True and not new_user:
        flash(u"Welcome back, {}.".format(_user.name), "success")
    else:
        flash(u"Error logging you in as {}, please try again later.".format(_user.name), "danger")
    return redirect(oid.get_next_url())


@users.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(u"You are now logged out.")
    return redirect(oid.get_next_url())


@users.route('/<int:user_id>/')
@users.route('/<int:user_id>/page/<int:page>/')
def user_page(user_id, page=1):
    user = User.query.get_or_404(user_id)
    mods = Mod.query.filter(Mod.authors.any(User.account_id == user.account_id)).filter_by(visibility="Pu", enabled=True, completed=True).paginate(page, 50)
    unlisted_mods = Mod.query.filter(Mod.authors.any(User.account_id == user.account_id)).filter_by(visibility="Pr", enabled=True, completed=True).paginate(page, 20)
    hidden_mods = None
    if user == current_user or current_user.is_admin():
        hidden_mods = Mod.query.filter(Mod.authors.any(User.account_id == user.account_id)).filter_by(visibility="H", enabled=True, completed=True).paginate(page, 10)
    return render_template('users/page.html', user=user, mods=mods, unlisted_mods=unlisted_mods, hidden_mods=hidden_mods, title=user.name)