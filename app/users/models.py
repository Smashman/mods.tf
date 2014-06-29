from app import db, steam
from flask.ext.login import AnonymousUserMixin
import datetime


class AnonymousUser(AnonymousUserMixin):
    user_class = 0

    def update_steam(self):
        return False


class User(db.Model):
    __tablename__ = "users"
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(256, collation="utf8_swedish_ci"))
    profile_url = db.Column(db.String(128))
    avatar_small = db.Column(db.String(128))
    avatar_medium = db.Column(db.String(128))
    avatar_large = db.Column(db.String(128))
    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    user_class = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        "order_by": [db.asc(joined)]
    }

    def __init__(self, account_id=None, steam_info=None, enabled=True):
        self.account_id = account_id
        if steam_info:
            self.name = steam_info.persona
            self.profile_url = steam_info.profile_url
            self.avatar_small = steam_info.avatar_small
            self.avatar_medium = steam_info.avatar_medium
            self.avatar_large = steam_info.avatar_large
        else:
            self.name = account_id
        self.enabled = enabled

    def __repr__(self):
        return self.name

    def get_id(self):
        return unicode(self.account_id)

    def is_active(self):
        return self.enabled

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @property
    def steam_id(self):
        return self.id + 76561197960265728