from . import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html', mods=[
        {
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer",
            "size":"large"
        },
        {
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "name":"disco_shirt",
            "author":"NeoDement, Spark Wire, Square",
            "pretty_name":"Groovy Garment",
            "mod_class": "demo"
        },
        {
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer"
        },
        {
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "name":"disco_shirt",
            "author":"NeoDement, Spark Wire, Square",
            "pretty_name":"Groovy Garment",
            "mod_class": "demo"
        },
        {
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "mod_class": "all-class",
            "downloads": "242",
            "replacements": "53"
        },
        {
            "name":"engi_banditana",
            "author":u"Spark Wire, R\u25B2in, Metabolic",
            "pretty_name":"The Farmer's Collective",
            "mod_class": "engineer"
        },
        {
            "name":"battle_bowler",
            "author":"donhonk, Sky, Metabolic",
            "pretty_name":"Battle Bowler",
            "mod_class": "demo",
            "downloads": "242",
            "replacements": "53"
        }
    ])