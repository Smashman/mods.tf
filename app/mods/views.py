from flask import Blueprint, send_from_directory, abort

mods = Blueprint("mods", __name__, url_prefix="/mods")


@mods.route('/images/<string:name>_<int:img_id>/')
def mod_image(name, img_id):
    print name
    print img_id
    if '..' in name or name.startswith('/'):
        abort(404)
    return send_from_directory('/home/ben/Documents/mod_files/'+name, 'img_'+str(img_id)+'.jpg', as_attachment=True)