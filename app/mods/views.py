from flask import Blueprint, send_from_directory, abort, render_template, request, flash, redirect, url_for, current_app
from app import db, workshopzips
from flask.ext.uploads import UploadNotAllowed
from flask.ext.login import current_user, login_required
from ..utils.utils import extract_and_image, package
from ..tf2.models import TF2Item
from models import Mod

mods = Blueprint("mods", __name__, url_prefix="/mods")


@mods.route('/upload/', methods=['GET', 'POST'])
@login_required
def mod_upload():
    if request.method == 'POST' and 'workshop_zip' in request.files:
        try:
            filename = workshopzips.save(request.files['workshop_zip'])
            mod_info = Mod(zip_file=filename, author=current_user)
            db.session.add(mod_info)
            db.session.commit()
            result = extract_and_image(filename, mod_info)
            if result:
                db.session.add(result)
                db.session.commit()
                return redirect(url_for('mods.mod_settings', mod_id=result.id))
        except UploadNotAllowed:
            flash("Only zips can be uploaded.", "danger")
    return render_template('mods/upload.html')


@mods.route('/images/<int:mod_id>/')  # TODO: Consider better methods of doing this
def mod_image(mod_id):
    return send_from_directory(current_app.config['OUTPUT_FOLDER_LOCATION'] + '/' + str(mod_id), 'backpack_icon_large.png',
                               as_attachment=True)


@mods.route('/download/')
def download():
    return render_template('mods/download.html')


@mods.route('/package/<int:mod_id>_<int:defindex>')
def package_mod(mod_id, defindex):
    mod = Mod.query.get_or_404(mod_id)
    replacement = TF2Item.query.get_or_404(defindex)
    package(mod, replacement)
    return render_template('mods/packaged.html')

@mods.route('/<int:mod_id>/settings/')
def mod_settings(mod_id):
    mod = Mod.query.get(mod_id)
    return render_template('construction.html', title="{} settings page - Under construction".format(mod.pretty_name))


@mods.route('/<int:mod_id>/')
def mod_page(mod_id):
    return render_template('construction.html', title="Under Construction")