from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('settings')
app.config.from_pyfile('settings.py')

# Setup debugtoolbar if we're in debug mode.
if app.debug:
    from flask.ext.debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

import views