from flask.ext.assets import Bundle, Environment
from .. import app
from os.path import abspath, join

bundles = {
    'main_css': Bundle(
        'lib/normalize-css/normalize.css',
        Bundle(
            'sass/main.sass',
            filters='sass',
            depends='sass/*.sass'
        ),
        output='../static/css/main.css',
    ),
    'main_js': Bundle(
        'js/main.js',
        output='../static/js/main.js',
        filters='jsmin'
    )
}

assets = Environment(app)
assets.load_path = [abspath(join(app.root_path, 'assets'))]
assets.cache = abspath(join(app.root_path, 'assets/cache'))
assets.register(bundles)