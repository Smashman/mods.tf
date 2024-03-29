import ntpath
import os
import steam
import zipfile
import shutil
from subprocess import check_call, CalledProcessError
from flask import flash, current_app, abort
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from ..tf2.models import all_classes, TF2BodyGroup, TF2EquipRegion
from ..mods.models import ModClassModel, ModImage
from ..models import get_or_create
from app import db, sentry


def list_from_vdf_dict(dictionary):
    return_list = []
    for dict_item, number in dictionary.items():
        if number is not None and number > 0:
            return_list.append(dict_item)
    return return_list


def extract_and_image(zip_in, db_record):
    """
    Extracts the uploaded zip files and generates an imagine and thumbnail from the given files.

    :param zip_in:
    :return:
    """
    input_folder = current_app.config['UPLOADED_WORKSHOPZIPS_DEST']
    output_folder = current_app.config['OUTPUT_FOLDER_LOCATION']
    mod_id = db_record.id

    print "Starting conversion: {}".format(zip_in)
    zip_filename = os.path.join(input_folder, zip_in)

    # If we have a zip file, grab the manifest
    if zipfile.is_zipfile(zip_filename):
        with zipfile.ZipFile(zip_filename, "r") as zip_file:
            if sum(f.file_size for f in zip_file.infolist()) < 105000000:
                try:
                    print "Opening manifest"
                    manifest_stream = zip_file.open('manifest.txt')
                    manifest_str = BytesIO(manifest_stream.read())
                    manifest = steam.vdf.load(manifest_str).get('asset')
                except KeyError:
                    flash("No manifest, please upload a Workshop zip.", "danger")
                    return
                except zipfile.BadZipfile:
                    flash("Archive is corrupt, please try repackaging your item before trying again.", "danger")
                    return
                print "Converting manifest. vdf -> dict"
            else:
                flash("Zip is too large when extracted, min size is ~100MB", "danger")
                return
    else:
        flash('Not a zip: {}'.format(zip_filename), "danger")
        return

    name = manifest['name']
    try:
        icon = manifest['ImportSession']['icon']
    except KeyError:
        icon = None

    if icon:
        # 'icon' can contain a lot of backslashes for reasons unknown to man, we'll get rid of them here.
        icon = ntpath.normpath(icon.replace('\\', ntpath.sep))
        iconUnix = os.path.normpath(icon.replace('\\', os.path.sep))

    # List of files we want to extract and later pack into a VPK
    to_extract = []

    # Start extracting
    print "Start extracting"
    with zipfile.ZipFile(zip_filename) as zip_open:
        for infile in zip_open.namelist():
            # Only extract the contents of the game, materials or models folder
            allowed_extracts = ['game', 'materials', 'models']
            if '..' in infile or infile.startswith('/'):
                flash("Error", "danger")
                return
            if ntpath.dirname(infile).split(ntpath.sep)[0] in allowed_extracts:
                to_extract.append(infile)

        # How many to extract
        print "{} files to extract.".format(len(to_extract))

        # Do extractings
        print "Extracting."
        safe_name = secure_filename(name)
        folder_name = "{mod_id}".format(mod_id=mod_id)
        os.path.altsep = '\\'
        zip_open.extractall(os.path.join(output_folder, folder_name), to_extract)

        if icon:
            # Load the icon into a byte stream
            print "Reading TGA image."
            try:
                tga_f = BytesIO(zip_open.read(iconUnix))
            except KeyError:
                tga_f = BytesIO(zip_open.read(icon))
            img = Image.open(tga_f)

            # Save the image as a PNG
            print "Saving large PNG image"
            filename = "backpack_icon_large.png"
            img.save(os.path.join(output_folder, folder_name, filename))
            backpack_icon_large = ModImage(filename, db_record.id, 0)
            db.session.add(backpack_icon_large)

            # Resize the image to make a thumbnail
            print "Resizing image"
            img.thumbnail((128, 128), Image.ANTIALIAS)

            # Save the thumbnail
            print "Saving small PNG image"
            filename = "backpack_icon.png"
            img.save(os.path.join(output_folder, folder_name, filename))
            backpack_icon = ModImage(filename, db_record.id, 1)
            db.session.add(backpack_icon)

    # Fetch desired item info from manifest

    items_game_info = manifest['ImportSession']['ItemSchema']

    equip_regions = []
    equip_region = items_game_info.get('equip_region')
    if equip_region:
        equip_regions.append(equip_region)
    else:
        equip_region_dict = items_game_info.get('equip_regions')
        if equip_region_dict:
            equip_regions += list_from_vdf_dict(equip_region_dict)

    visuals = items_game_info.get('visuals')
    bodygroups = []
    if visuals:
        bodygroups_dict = visuals.get('player_bodygroups')
        if bodygroups_dict:
            bodygroups += list_from_vdf_dict(bodygroups_dict)

    used_by_classes = items_game_info.get('used_by_classes')
    used_by_classes = list_from_vdf_dict(used_by_classes)
    used_by_classes = [i.lower() for i in used_by_classes]
    model_player = items_game_info.get('model_player')

    class_models = {}

    if used_by_classes and len(used_by_classes) is 1:
        if model_player:
            class_models.update({used_by_classes[0].lower(): model_player})
        else:
            return

    elif not used_by_classes or len(used_by_classes) > 1:
        if not used_by_classes:
            used_by_classes = all_classes
        model_player_per_class = items_game_info.get('model_player_per_class')
        model_player_per_class = dict((k.lower(), v) for k, v in model_player_per_class.iteritems())
        for tf2_class in used_by_classes:
            if tf2_class.title() in all_classes:
                if model_player_per_class:
                    class_model = model_player_per_class.get(tf2_class)
                elif model_player:
                    class_model = model_player
                else:
                    continue
                class_and_model = {tf2_class: class_model}
                class_models.update(class_and_model)

    # Update database record

    db_record.name = safe_name
    db_record.pretty_name = manifest['ImportSession']['name']
    db_record.manifest_steamid = int(manifest['steamid'], 16)
    db_record.item_slot = "misc"  # Only miscs have Workshop zips to date
    db_record.image_inventory = items_game_info.get('image_inventory')
    if bodygroups:
        for bodygroup in bodygroups:
            bg_db = TF2BodyGroup.query.get(bodygroup)
            if bg_db:
                db_record.bodygroups.append(bg_db)
    if equip_regions:
        for er in equip_regions:
            er_db = TF2EquipRegion.query.get(er)
            if er_db:
                db_record.equip_regions.append(er_db)
    if class_models:
        for class_name, model in class_models.items():
            db_record.class_model[class_name] = (get_or_create(db.session, ModClassModel, mod_id=mod_id,
                                                                class_name=class_name, model_path=model))

    # And we're fin
    print "Done: {}".format(db_record.zip_file)
    db_record.completed = True
    return db_record


def vpk_package(folder):
    try:
        check_call([os.path.abspath(current_app.config['VPK_BINARY_PATH']), folder])
    except CalledProcessError:
        sentry.captureException()
        abort(500)
    shutil.rmtree(folder)


def rename_copy(ext_list, dest_format):
    for extension in ext_list:
        for mod_path, replacement_path in dest_format.items():
            to_rename = mod_path.format(ext=extension)
            rename_dest = replacement_path.format(ext=extension)

            dest_directory = os.path.dirname(rename_dest)
            if not os.path.exists(dest_directory):
                os.makedirs(dest_directory)

            shutil.copyfile(to_rename, rename_dest)


def backpack_icon(output_folder, input_folder, backpack_extensions, image_inventory):
    model_material_copy = os.path.abspath(os.path.join(output_folder, "materials/models/workshop/"))
    backpack_material_copy = os.path.abspath(os.path.join(output_folder, "materials/backpack/workshop/"))

    model_workshop_materials = os.path.abspath(os.path.join(input_folder, "materials/models/workshop/"))
    backpack_workshop_materials = os.path.abspath(os.path.join(input_folder, "materials/backpack/workshop/"))
    shutil.copytree(model_workshop_materials, model_material_copy)
    shutil.copytree(backpack_workshop_materials, backpack_material_copy)

    for extension in backpack_extensions:
        os.remove(image_inventory.format(ext=extension))


def package_mod_to_item(mod, replacement):
    model_extensions = [
        ".mdl",
        ".dx80.vtx",
        ".dx90.vtx",
        ".sw.vtx",
        ".vvd"
    ]
    backpack_extensions = [
        ".vmt",
        "_large.vmt"
    ]
    mod_all_class = False
    replacement_all_class = False

    if len(mod.class_model) > 1:
        mod_all_class = True

    if len(replacement.class_model) > 1:
        replacement_all_class = True

    mod_name = mod.pretty_name
    if mod_name.startswith("The "):
        mod_name = mod_name[4:]
    mod_name = secure_filename(mod_name).lower()
    item_name = secure_filename(replacement.item_name).lower()

    mod_folder = os.path.join(current_app.config['OUTPUT_FOLDER_LOCATION'],
                              "{mod_id}".format(mod_id=mod.id, mod_name=mod.name))

    package_name = 'mods_tf_{name}_{item_name}'.format(name=mod_name, item_name=item_name)

    input_folder = os.path.join(mod_folder, 'game')
    output_folder = os.path.join(mod_folder, package_name)

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    model_player = {}

    for class_name, class_model in replacement.class_model.items():
        try:
            mod_class_model = mod.class_model[class_model.class_name]
            model_path = class_model.model_path.replace(".mdl", "{ext}")
            mod_model_path = mod_class_model.model_path.replace(".mdl", "{ext}")
            model_path = os.path.abspath(os.path.join(output_folder, model_path))
            mod_model_path = os.path.abspath(os.path.join(input_folder, mod_model_path))
            model_player[mod_model_path] = model_path
        except KeyError:
            pass
    image_inventory = {}

    image_inventory_mod = os.path.abspath(os.path.join(input_folder, "materials/", mod.image_inventory + "{ext}"))
    image_inventory_replacement = os.path.abspath(
        os.path.join(output_folder, "materials/", replacement.image_inventory + "{ext}")
    )
    image_inventory[image_inventory_mod] = image_inventory_replacement

    image_inventory_remove = os.path.abspath(os.path.join(output_folder, "materials/", mod.image_inventory + "{ext}"))

    backpack_icon(output_folder, input_folder, backpack_extensions, image_inventory_remove)
    rename_copy(backpack_extensions, image_inventory)
    if mod_all_class or replacement_all_class:
        rename_copy(model_extensions, model_player)
    else:
        rename_copy(model_extensions, model_player)

    vpk_package(output_folder)
    return package_name + ".vpk"