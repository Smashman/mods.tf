from . import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html', mods=[
        {
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble, NassimO, BANG!, void~, BADGERPIG, Frying Dutchman",
            "pretty_name":"Arctic Aviator",
            "mod_class": "heavy"
        },
        {
            "name":"arctic_aviator",
            "author":"NeoDement, Kibble",
            "pretty_name":"Arctic Aviator",
            "classes":"small"
        }
    ])