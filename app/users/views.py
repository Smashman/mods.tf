from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app, g
from app import oid, steam, db, login_manager
from models import User, AnonymousUser
from flask.ext.login import login_user, logout_user, current_user, login_required

users = Blueprint("users", __name__, url_prefix="/users")

login_manager.anonymous_user = AnonymousUser


# User authentication
@login_manager.user_loader
def load_user(user_id):
    _user = User.query.get(user_id)
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
    steam_id = long(resp.identity_url.replace("http://steamcommunity.com/openid/id/", ""))
    account_id = int(steam_id & 0xFFFFFFFF)
    _user = User.query.get(account_id)
    new_user = False

    if not _user:
        steam_info = steam.user.profile(steam_id)
        _user = User(account_id, steam_info)
        new_user = True
        db.session.add(_user)
        db.session.commit()

    login_attempt = login_user(_user, remember=True)
    if login_attempt is True and new_user:
        flash(u"Welcome to mods.tf, {}!".format(_user.name), "success")
    elif login_attempt is True and not new_user:
        flash(u"Welcome back, {}.".format(_user.name), "success")
    elif not _user.is_active():
        flash(u"Cannot log you in, {}. You are banned.".format(_user.name), "danger")
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
def user_page(user_id):
    return render_template('construction.html', title="Under Construction")


@users.route('/<int:user_id>/settings/')
def user_settings(user_id):
    return render_template('construction.html', title="Under Construction")