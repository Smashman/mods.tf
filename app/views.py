from . import app, db
from flask import render_template, url_for
from mods.models import Mod


@app.route('/')
def index():
    mods = Mod.query.filter(Mod.visibility == "Pu").filter(Mod.enabled == True).all()
    return render_template('index.html', mods=mods)


@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(500)  # Internal server error.
def internal_error(error):
    error_descriptions = {
        401: {"quote": "\"No way!\" &dash; Scout",
              "description": "You are not authorised to access this page. "
                             "<a href=\"{}\">Try logging in.</a>".format(url_for('users.login'))},
        403: {"quote": "\"Nope.\" &dash; Engineer",
              "description": "Access to this is resource is forbidden."},
        404: {"quote": "\"Well, this was a disappointment!\" &dash; Spy"},
        500: {"quote": "\"Tell me, where did we go so wrong?\" &dash; Heavy",
              "description": "The error has been reported and will be investigated."},
    }
    return_to_main_menu = " Please return to <a href=\"{}\">the main page</a>.".format(url_for('index'))
    return_to_main_menu_list = [403, 404, 500]
    try:
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