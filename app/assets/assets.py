from flask.ext.assets import Bundle, Environment
from .. import app
from os.path import abspath, join

bundles = {
    'main_css': Bundle(
        'sass/main.sass',
        filters='sass',
        output='../static/css/main.css'
    ),
    'main_js': Bundle(
        'lib/jquery/dist/jquery.min.js',
        Bundle(
            'js/main.js',
            filters='jsmin'
        ),
        output='../static/js/main.js'
    )
}

assets = Environment(app)
assets.load_path = [abspath(join(app.root_path, 'assets'))]
assets.cache = abspath(join(app.root_path, 'assets/cache'))
assets.register(bundles)