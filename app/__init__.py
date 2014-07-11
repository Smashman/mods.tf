from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.uploads import UploadSet, configure_uploads
import steam

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('settings')
app.config.from_pyfile('settings.py')

# Setup debugtoolbar, if we're in debug mode.
if app.debug:
    from flask.ext.debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

# Flask extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
oid = OpenID(app)
workshopzips = UploadSet('workshopZips', 'zip')

# Setup steamodd
steam.api.key.set(app.config['STEAM_API_KEY'])
steam.api.socket_timeout.set(5)

# Setup Flask-Uploads
configure_uploads(app, workshopzips)

# Views
import views

# Blueprints
from app.users.views import users as users_blueprint
from app.mods.views import mods as mods_blueprint
from app.tf2.views import tf2 as tf2_blueprint

# TF2 Schema
from app.tf2.models import TF2Item, TF2EquipRegion, TF2BodyGroup

app.register_blueprint(users_blueprint)
app.register_blueprint(mods_blueprint)
app.register_blueprint(tf2_blueprint)

# Assets
from assets import assets