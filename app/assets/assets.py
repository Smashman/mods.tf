from flask.ext.assets import Bundle, Environment
from .. import app
from os.path import abspath, join

bundles = {
    'main_css': Bundle(
        Bundle(
            'sass/main.sass',
            filters='sass',
            depends='sass/*.sass'
        ),
        output='../static/css/main.css'
    ),
    'main_js': Bundle(
        Bundle(
            'js/main.js',
            filters='jsmin'
        ),
        output='../static/js/main.js'
    ),
    'download_js': Bundle(
        'js/download.js',
        output='../static/js/download.js',
        filters='jsmin'
    )
}

assets = Environment(app)
assets.load_path = [abspath(join(app.root_path, 'assets'))]
assets.cache = abspath(join(app.root_path, 'assets/cache'))
assets.register(bundles)