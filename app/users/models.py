from app import db, steam
from steam.api import HTTPError, HTTPTimeoutError
from flask.ext.login import AnonymousUserMixin
import datetime


class AnonymousUser(AnonymousUserMixin):
    user_class = 0

    @staticmethod
    def update_steam():
        return False

    @staticmethod
    def is_admin():
        return False

    @staticmethod
    def is_uploader():
        return False


class User(db.Model):
    __tablename__ = "users"
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(512, collation="utf8mb4_unicode_ci"), default=account_id)
    profile_url = db.Column(db.String(128))
    avatar_small = db.Column(db.String(128))
    avatar_medium = db.Column(db.String(128))
    avatar_large = db.Column(db.String(128))
    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    next_steam_check = db.Column(db.DateTime, default=datetime.datetime.utcnow() + datetime.timedelta(hours=4))
    user_class = db.Column(db.Integer, default=0)
    upload_credits = db.Column(db.Integer, default=0)
    signed_in = db.Column(db.Boolean, default=True)
    enabled = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        "order_by": [db.asc(joined)]
    }

    def __init__(self, account_id=None, signed_in=None, last_seen=None):
        self.account_id = account_id
        self.signed_in = signed_in
        self.last_seen = last_seen
        self.fetch_steam_info()

    def __repr__(self):
        return self.name

    def get_id(self):
        return unicode(self.account_id)

    def is_active(self):
        return self.enabled

    @staticmethod
    def is_anonymous():
        return False

    @staticmethod
    def is_authenticated():
        return True

    def is_admin(self):
        return True if self.user_class > 1 else False

    def is_uploader(self):
        return True if self.upload_credits > 0 or self.upload_credits == -1 or self.is_admin() else False

    def update_last_seen(self):
        now = datetime.datetime.utcnow()
        if not self.next_steam_check:
            self.next_steam_check = datetime.datetime.utcnow()
        self.last_seen = now
        if self.next_steam_check < now:
            self.fetch_steam_info()
        db.session.add(self)
        db.session.commit()

    def fetch_steam_info(self):
        steam_info = steam.user.profile(self.steam_id)
        self.update_steam_info(steam_info)

    def update_steam_info(self, steam_info):
        try:
            self.name = steam_info.persona
            self.profile_url = steam_info.profile_url
            self.avatar_small = steam_info.avatar_small
            self.avatar_medium = steam_info.avatar_medium
            self.avatar_large = steam_info.avatar_large
            self.next_steam_check = datetime.datetime.utcnow() + datetime.timedelta(hours=4)
        except (HTTPError, HTTPTimeoutError):
            self.next_steam_check = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    @property
    def steam_id(self):
        return self.account_id + 76561197960265728

    @property
    def perma_profile_url(self):
        return "http://steamcommunity.com/profiles/{}".format(self.steam_id)