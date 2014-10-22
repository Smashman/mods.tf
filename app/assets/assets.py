from flask.ext.assets import Bundle, Environment
from .. import app
from os.path import abspath, join

bundles = {

    # TEAM FORTRESS 2 THEMES
    'tf2_css': Bundle(
        'sass/main.sass',
        depends='sass/*.sass',
        filters='sass',
        output='../static/css/tf2.css'
    ),
    'tf2_halloween_css': Bundle(
        'sass/halloween.sass',
        depends='sass/*.sass',
        filters='sass',
        output='../static/css/tf2_halloween.css'
    ),

    # DOTA 2 THEMES
    'dota_css': Bundle(
        'sass/dota.sass',
        depends='sass/*.sass',
        filters='sass',
        output='../static/css/dota.css'
    ),

    # OTHER
    'multiple-select': Bundle(
        'lib/multiple-select/multiple-select.css',
        #filters='cssmin',
        output='../static/css/multiple-select.css'
    ),

    # JAVASCRIPT
    'main_js': Bundle(
        'lib/multiple-select/jquery.multiple.select.js',
        'js/main.js',
        filters='jsmin',
        output='../static/js/main.js'
    ),
    'download_js': Bundle(
        'js/download.js',
        output='../static/js/download.js',
        filters='jsmin'
    ),
    'edit_js': Bundle(
        'js/edit.js',
        output='../static/js/edit.js',
        filters='jsmin'
    ),
    'search_js': Bundle(
        'js/search.js',
        output='../static/js/search.js',
        filters='jsmin'
    )
}

assets = Environment(app)
assets.load_path = [abspath(join(app.root_path, 'assets'))]
assets.cache = abspath(join(app.root_path, 'assets/cache'))
assets.register(bundles)