from . import app, db
from flask import render_template, url_for
from tf2.models import TF2Item, TF2ClassModel


@app.route('/')
def index():
    return render_template('index.html', mods=[
        {
            "id":1,
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer",
            "size":"large"
        },
        {
            "id":1,
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "id":1,
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "id":1,
            "name":"disco_shirt",
            "author":"NeoDement, Spark Wire, Square",
            "pretty_name":"Groovy Garment",
            "mod_class": "demo"
        },
        {
            "id":1,
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "id":1,
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer"
        },
        {
            "id":1,
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "id":1,
            "name":"disco_shirt",
            "author":"NeoDement, Spark Wire, Square",
            "pretty_name":"Groovy Garment",
            "mod_class": "demo"
        },
        {
            "id":1,
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "id":1,
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer"
        },
        {
            "id":1,
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        }
    ])


@app.route('/beards/<string:class_name>')
def beards(class_name):
    beards_query = TF2Item.query.filter(~TF2Item.class_model.any(TF2ClassModel.class_name!=class_name))\
        .filter(TF2Item.equip_regions.any(equip_region='beard')).all()
    return render_template('beard_test.html', beards=beards_query)


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