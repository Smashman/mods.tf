from flask import Blueprint, send_from_directory, abort, render_template, request, flash, redirect, url_for,\
    current_app
from app import db, workshopzips
from flask.ext.uploads import UploadNotAllowed
from flask.ext.login import current_user, login_required
from ..utils.utils import extract_and_image, package_mod_to_item
from ..tf2.models import TF2Item, TF2BodyGroup, TF2EquipRegion, TF2Class
from models import Mod, ModClassModel
from forms import ItemSearch

mods = Blueprint("mods", __name__, url_prefix="/mods")

enabled_mods = Mod.query.filter(Mod.visibility == "Pu").filter(Mod.enabled == True)


@mods.route('/<int:mod_id>/')
def page(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    return render_template('mods/page.html', mod=mod)


@mods.route('/<int:mod_id>/settings/')
def settings(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    return render_template('construction.html', title="{} settings page - Under construction".format(mod.pretty_name))


@mods.route('/search/')
def search():
    equip_region = request.args.get('equip_region')
    bodygroup = request.args.get('bodygroup')
    mods = enabled_mods
    if equip_region:
        mods = mods.filter(Mod.equip_regions.any(TF2EquipRegion.equip_region == equip_region))
    if bodygroup:
        mods = mods.filter(Mod.bodygroups.any(TF2BodyGroup.bodygroup == bodygroup))
    mods = mods.paginate(1, 30)
    return render_template('mods/search.html', mods=mods)


@mods.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
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
def image(mod_id):
    print(mod_id)
    return send_from_directory(current_app.config['OUTPUT_FOLDER_LOCATION'] + '/' + str(mod_id), 'backpack_icon_large.png',
                               as_attachment=True)


@mods.route('/<int:mod_id>/download/')
def download(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    if mod.enabled is False or mod.visibility != "Pu":
        abort(404)
    classes = mod.class_model

    item_search = ItemSearch()
    any_choice = [(0, "Any")]

    class_choices = [(_class.class_name, _class.class_name.capitalize()) for key, _class in classes.items()]
    class_choices.sort()
    item_search.classes.data = [_class for _class in classes]
    item_search.bodygroups.data = ["0"]
    item_search.bodygroups.data = [bodygroup.bodygroup for bodygroup in mod.bodygroups]
    item_search.equip_regions.data = [equip_region.equip_region for equip_region in mod.equip_regions]

    equip_regions = TF2EquipRegion.query.all()
    bodygroups = TF2BodyGroup.query.all()

    item_search.classes.choices = class_choices
    item_search.equip_regions.choices = any_choice + [(equip_region.equip_region, equip_region.full_name or equip_region.equip_region.capitalize()) for equip_region in equip_regions]
    item_search.bodygroups.choices = any_choice + [(bodygroup.bodygroup, bodygroup.full_name or bodygroup.bodygroup.capitalize()) for bodygroup in bodygroups]

    return render_template('mods/download.html', item_search=item_search, mod_id=mod_id)


@mods.route('/<int:mod_id>/package/<int:defindex>/')
def package(mod_id, defindex):
    mod = Mod.query.get_or_404(mod_id)
    replacement = TF2Item.query.get_or_404(defindex)
    file_name = package_mod_to_item(mod, replacement)
    return render_template('mods/packaged.html', mod=mod, replacement=replacement,
                           download_url=file_name)