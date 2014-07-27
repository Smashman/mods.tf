from flask.ext.assets import Bundle, Environment
from webassets.filter import get_filter
from .. import app
from os.path import abspath, join

bundles = {
    'main_css': Bundle(
        'lib/multiple-select/multiple-select.css',
        Bundle(
            'sass/main.sass',
            depends='sass/*.sass',
            filters='sass'
        ),
        output='../static/css/main.css'
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