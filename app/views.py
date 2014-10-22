import os
from . import app, db
from flask import render_template, url_for, send_from_directory
from mods.models import Mod
from mods.functions import get_mod_stats


@app.route('/')
def index():
    mods = Mod.query.filter_by(visibility="Pu", enabled=True, completed=True).limit(18).all()
    for mod in mods:
        mod_stats = get_mod_stats(mod)
    return render_template('index.html', mods=mods)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/credits/')
def additional_credits():
    return render_template('credits.html')


@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(405)  # Method not allowed
@app.errorhandler(500)  # Internal server error.
def internal_error(error):
    error_descriptions = {
        401: {"quote": "\"No way!\" &ndash; Scout",
              "description": "You are not authorised to access this page. "
                             "<a href=\"{}\">Try logging in.</a>".format(url_for('users.login'))},
        403: {"quote": "\"Nope.\" &ndash; Engineer",
              "description": "Access to this is resource is forbidden."},
        404: {"quote": "\"Well, this was a disappointment!\" &ndash; Spy"},
        500: {"quote": "\"Tell me, where did we go so wrong?\" &ndash; Heavy",
              "description": "The error has been reported and will be investigated."},
    }
    return_to_main_menu = " Please return to <a href=\"{}\">the main page</a>.".format(url_for('index'))
    return_to_main_menu_list = [403, 404, 500]
    try:
        if error.code == 405:
            error.code = 404
        error_description = error_descriptions.get(error.code)
        error.quote = error_description.get("quote") or None
        error.description = error_description.get("description") or error.description
        if error.code in return_to_main_menu_list:
            error.description += return_to_main_menu
    except AttributeError:
        db.session.rollback()

        error.code = 500
        error.name = "Internal Server Error"
        error_description = error_descriptions.get(error.code)
        error.quote = error_description.get("quote") or None
        error.description = error_description.get("description") or None

    title = "{} {}".format(error.code, error.name)
    return render_template("error.html", error=error, title=title), error.code