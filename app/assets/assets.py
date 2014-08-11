from flask.ext.assets import Bundle, Environment
from .. import app
from os.path import abspath, join

bundles = {
    'tf2_css': Bundle(
        'sass/tf2.sass',
        depends='sass/*.sass',
        filters='sass',
        output='../static/css/tf2.css'
    ),
    'dota_css': Bundle(
        'sass/dota.sass',
        depends='sass/*.sass',
        filters='sass',
        output='../static/css/dota.css'
    ),
    'multiple-select': Bundle(
        'lib/multiple-select/multiple-select.css',
        #filters='cssmin',
        output='../static/css/multiple-select.css'
    ),
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
    )
}

assets = Environment(app)
assets.load_path = [abspath(join(app.root_path, 'assets'))]
assets.cache = abspath(join(app.root_path, 'assets/cache'))
assets.register(bundles)