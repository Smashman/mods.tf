from flask import Blueprint, send_from_directory, abort, render_template, request, flash, redirect, url_for,\
    current_app
from app import db, workshopzips, sentry
from flask.ext.uploads import UploadNotAllowed
from flask.ext.login import current_user, login_required
from ..utils.utils import extract_and_image, package_mod_to_item
from ..tf2.models import TF2Item, TF2BodyGroup, TF2EquipRegion
from ..tf2.views import format_query, item_search
from ..users.models import User
from models import Mod, ModPackage, PackageDownload, ModImage, ModAuthor
from forms import ItemSearch, EditMod
from functions import check_mod_permissions, check_edit_permissions, new_author, get_mod_stats
from ..functions import remove_duplicates
import datetime
import os
import json

mods = Blueprint("mods", __name__, url_prefix="/mods")

enabled_mods = Mod.query.filter_by(visibility="Pu", completed=True, enabled=True)


@mods.route('/')
@mods.route('/page/<int:page>/')
def all_mods(page=1):
    _mods = enabled_mods.paginate(page, 20)
    for mod in _mods.items:
        mod_stats = get_mod_stats(mod)
        mod.downloads = mod_stats.get("downloads")
        mod.replacements = mod_stats.get("replacements")
    return render_template('mods/all_mods.html', mods=_mods, title="All mods")


@mods.route('/<int:mod_id>/')
@mods.route('/<int:mod_id>/page/<int:page>/')
def page(mod_id, page=1):
    mod = Mod.query.get_or_404(mod_id)
    check_mod_permissions(mod)
    mod_stats = get_mod_stats(mod)
    mod.downloads = mod_stats.get("downloads")
    mod.replacements = mod_stats.get("replacements")

    item_results = format_query(mod_stats.get("item_query"), mod.id, page)

    item_search_form = ItemSearch()

    classes = mod.class_model
    class_array = ["scout", "soldier", "pyro", "demoman", "heavy", "engineer", "sniper", "medic", "spy"]
    sorted_classes = sorted([(_class.class_name, _class.class_name.capitalize())
                            for key, _class in classes.items()], key=lambda c: class_array.index(c[0]))

    item_search_form.equip_regions.query = TF2EquipRegion.query.all()
    item_search_form.bodygroups.query = TF2BodyGroup.query.all()
    item_search_form.classes.choices = sorted_classes

    item_search_form.classes.data = [_class for _class in classes]
    item_search_form.bodygroups.data = [bodygroup for bodygroup in mod.bodygroups]
    item_search_form.equip_regions.data = [equip_region for equip_region in mod.equip_regions]

    return render_template('mods/page.html', mod=mod, item_search=item_search_form, mod_id=mod.id,
                           item_results=item_results.get('items'), page=page, title=mod.pretty_name,
                           sorted_classes=sorted_classes)


@mods.route('/<int:mod_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    check_edit_permissions(mod)
    edit_form = EditMod()

    edit_form.equip_regions.query = TF2EquipRegion.query.all()
    edit_form.bodygroups.query = TF2BodyGroup.query.all()

    package_formats = [("vpk", "VPK")]

    edit_form.package_format.choices = package_formats

    if mod.visibility != "Pu":
        edit_form.publish.label.text += " and Publish!"

    if edit_form.workshop_id.data == "":
        edit_form.workshop_id.data = None

    if edit_form.validate_on_submit():
        valid = True
        mod.pretty_name = edit_form.pretty_name.data
        mod.description = edit_form.description.data
        workshop_id = edit_form.workshop_id.data
        if workshop_id:
            try:
                if "http://steamcommunity.com/sharedfiles/filedetails/" in workshop_id:
                    from urlparse import urlparse, parse_qs
                    workshop_id = parse_qs(urlparse(workshop_id).query).get("id")[0]
                    int(workshop_id)
                elif not int(workshop_id) > 0:
                    valid = False
                    edit_form.workshop_id.errors.append("Not a valid workshop ID.")
                    workshop_id = None
            except (ValueError, TypeError):
                    valid = False
                    edit_form.workshop_id.errors.append("Not a valid workshop ID.")
                    workshop_id = None
            mod.workshop_id = workshop_id
        if not workshop_id or workshop_id == "":
            mod.workshop_id = None

        mod.package_format = edit_form.package_format.data

        mod.bodygroups = []
        mod.equip_regions = []

        for bodygroup in edit_form.bodygroups.data:
            mod.bodygroups.append(TF2BodyGroup.query.get(bodygroup))

        for equip_region in edit_form.equip_regions.data:
            mod.equip_regions.append(TF2EquipRegion.query.get(equip_region))
        if edit_form.publish.data:
            mod.visibility = "Pu"

        authors_to_add = []
        for i, author in enumerate(edit_form.authors):
            authors_to_add.append((i, author.author.data))

        author_profiles = []
        for i, add_author in authors_to_add:
            if add_author:
                user_author_record = new_author(add_author)
                if isinstance(user_author_record, str):
                    edit_form.authors.entries[i].author.errors.append(user_author_record)
                    valid = False
                else:
                    author_profiles.append(user_author_record)

        if not current_user.is_admin() and current_user not in author_profiles:
            edit_form.authors.errors.append("You may not remove yourself as an author.")
            valid = False

        author_profiles = remove_duplicates(author_profiles)

        if valid:
            for i in range(0, len(mod.authors)):
                mod.authors.pop()
            for i, author_profile in enumerate(author_profiles):
                mod_author = ModAuthor(mod_id=mod.id, user_id=author_profile.account_id, order=i)
                db.session.add(mod_author)
            db.session.add(mod)
            db.session.commit()
            flash("Save successful.", "success")
            return redirect(url_for("mods.page", mod_id=mod.id))

    classes = [_class for _class in mod.class_model]

    edit_form.pretty_name.data = mod.pretty_name
    edit_form.workshop_id.data = mod.workshop_id
    edit_form.description.data = mod.description
    for i, author in enumerate(mod.authors):
        edit_form.authors[i].author.data = author.perma_profile_url
    edit_form.equip_regions.data = [equip_region for equip_region in mod.equip_regions]
    edit_form.bodygroups.data = [bodygroup for bodygroup in mod.bodygroups]

    classes_array = json.dumps(classes)

    count = item_search(
        classes=classes,
        bodygroups=[bodygroup.bodygroup for bodygroup in mod.bodygroups],
        equip_regions=[equip_region.equip_region for equip_region in mod.equip_regions]
    ).count()

    """if request.method == 'POST' and 'mod_image' in request.files:
        try:
            filename = modimages.save(request.files['mod_image'])
            print filename
        except UploadNotAllowed:
            flash("Only images can be uploaded.", "danger")
        <form method=POST enctype=multipart/form-data>
            <input type=file name=mod_image>
            <input type="submit" value="Submit">
        </form>"""
    return render_template('mods/edit.html', mod=mod, edit_form=edit_form, classes=classes_array, count=count,
                           title=u"Editing {}".format(mod.pretty_name))


@mods.route('/search/')
@mods.route('/search/page/<int:page>/')
def search(page=1):
    #equip_region = request.args.get('equip_region')
    #bodygroup = request.args.get('bodygroup')
    #mods = enabled_mods
    #if equip_region:
        #mods = mods.filter(Mod.equip_regions.any(TF2EquipRegion.equip_region == equip_region))
    #if bodygroup:
        #mods = mods.filter(Mod.bodygroups.any(TF2BodyGroup.bodygroup == bodygroup))
    #mods = mods.paginate(page, 30)
    #return render_template('mods/search.html', mods=mods, title="Search")
    return render_template('construction.html', mods=mods, title="Under construction")


@mods.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_uploader():
        abort(403)
    if request.method == 'POST' and 'workshop_zip' in request.files:
        filename = None
        workshop_zip = request.files['workshop_zip']
        workshop_zip.seek(0, os.SEEK_END)
        if workshop_zip.tell() == 0:
            flash("Please select a file to upload.", "danger")
            return redirect(url_for('.upload'))
        workshop_zip.seek(0)
        try:
            filename = workshopzips.save(workshop_zip)
        except UploadNotAllowed:
            flash("Please upload a gold star zip file.", "danger")
        mod_info = Mod(zip_file=filename, author=current_user)
        db.session.add(mod_info)
        db.session.commit()
        result = extract_and_image(filename, mod_info)
        if result:
            if current_user.upload_credits != -1:
                current_user.upload_credits = User.upload_credits - 1
            db.session.add(current_user)
            db.session.add(result)
            db.session.commit()
            flash(u"Hooray! {mod.pretty_name} has been uploaded and is almost ready to download. "
                  "Please check over the mod information and hit \"Publish!\", when you're satisfied."
                  "".format(mod=result), "success")
            return redirect(url_for('.edit', mod_id=result.id))
    return render_template('mods/upload.html', title="Upload a mod")


@mods.route('/<int:mod_id>/images/<int:type>/')  # TODO: Consider better methods of doing this
def image(mod_id, type):
    mod = Mod.query.get_or_404(mod_id)
    check_mod_permissions(mod)
    image = ModImage.query.filter_by(mod_id=mod_id, type=type).first()
    return send_from_directory(os.path.abspath(os.path.join(current_app.config['OUTPUT_FOLDER_LOCATION'], str(mod_id))),
                               image.filename,
                               as_attachment=True)


@mods.route('/<int:mod_id>/download/<int:defindex>/')
@login_required
def package(mod_id, defindex):
    mod_package = ModPackage.query.filter_by(mod_id=mod_id, defindex=defindex).first()
    mod = Mod.query.get_or_404(mod_id)
    replacement = TF2Item.query.get_or_404(defindex)
    if not current_user.is_admin():
        twenty_four_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        downloads_by_mod = PackageDownload.query.filter_by(user=current_user)\
            .filter(PackageDownload.downloaded >= twenty_four_hours_ago)\
            .outerjoin(ModPackage)\
            .filter(ModPackage.mod_id == mod_id)
        if downloads_by_mod.count() >= 15:
            flash(u"Download limit for {} reached. Please try again in 24 hours.".format(mod.pretty_name), "danger")
            sentry.captureMessage("User reached download limit for mod.")
            return redirect(url_for("mods.page", mod_id=mod_id))
        downloads_by_replacement = downloads_by_mod.filter(ModPackage.defindex == defindex)
        if downloads_by_replacement.count() >= 2:
            flash(u"Download limit for {} replacement reached. Please try again in 24 hours."
                  .format(replacement.item_name), "danger")
            sentry.captureMessage("User reached download limit for mod replacement.")
            return redirect(url_for("mods.page", mod_id=mod_id))
    if not mod_package:
        filename = package_mod_to_item(mod, replacement)
        long_date = False
        if datetime.datetime.utcnow() < mod.uploaded + datetime.timedelta(weeks=4):
            long_date = True
        mod_package = ModPackage(mod.id, replacement.defindex, filename, long_date)
        db.session.add(mod_package)
        db.session.commit()
    elif datetime.datetime.utcnow() > mod_package.expire_date:
        mod = mod_package.mod
        replacement = mod_package.replacement
        long_date = False
        if datetime.datetime.utcnow() < mod.uploaded + datetime.timedelta(weeks=4):
            long_date = True
        filename = package_mod_to_item(mod, replacement)
        mod_package.filename = filename
        mod_package.update_expire(long_date)
        mod_package.deleted = False
        db.session.add(mod_package)
        db.session.commit()
    else:
        mod = mod_package.mod
        filename = mod_package.filename
    download_record = PackageDownload(mod_package.id, current_user.account_id)
    db.session.add(download_record)
    db.session.commit()
    return send_from_directory(os.path.abspath(os.path.join(current_app.config['OUTPUT_FOLDER_LOCATION'], str(mod.id))),
                               filename,
                               as_attachment=True)