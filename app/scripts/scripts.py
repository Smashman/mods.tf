import steam
import urllib2
import datetime
import os
from steam.api import HTTPError
from .. import db
from ..models import get_or_create
from ..tf2.models import TF2Item, TF2Class, TF2BodyGroup, TF2ClassModel, TF2EquipRegion, all_classes
from ..tf2.functions import class_array
from ..mods.models import ModPackage, ModAuthor
from ..utils.utils import list_from_vdf_dict
from ..functions import combine_dicts
from flask import current_app


def insert_classes():
    for tf2_class in all_classes:
        get_or_create(db.session, TF2Class, class_name=tf2_class.lower())
    db.session.commit()


def update_tf2_items():
    update_completed = False

    insert_classes()

    bad_item_types = ["CheatDetector", "Tournament Medal", "Cursed Soul", "Badge"]
    bad_item_names = ["TF_GateBot_Light"]
    bad_defindexes = [5606,  # Damaged Capacitor (Not equippable)
                      8938,  # Glitched Circuit Board (Not equippable)
                      30143, 30144, 30145, 30146, 30147, 30148, 30149, 30150, 30151, 30152, 30153, 30154, 30155, 30156,
                      30157, 30158, 30159, 30160, 30161,  # Romevision cosmetics - Robots only
                      835, 836, 837, 838,  # Separate SD promo items
                      576  # Spine-Chilling Skull 2011 (Same model as Spine-Tingling Skull)
                      ]
    amend_equip_regions = {"hat": [162, 711, 712, 713], "belt_misc": [1011], "ring": [5075], "shirt": [1088]}

    for i in range(10):
        if not update_completed:
            print "Not completed. Trying again."
            try:
                schema = steam.api.interface("IEconItems_440").GetSchema(language="english").get("result")
                items_game_url = schema.get('items_game_url')
                items_game = steam.vdf.load(urllib2.urlopen(items_game_url)).get('items_game')
            except HTTPError:
                db.session.rollback()
                continue
            items = schema.get('items')
            print "{} items in schema. Starting loop".format(len(items))
            for item in items:
                if item.get('item_slot') == "misc" and item.get('item_type_name') not in bad_item_types:

                    defindex = item.get('defindex')

                    existing_item = TF2Item.query.get(defindex)

                    if defindex in bad_defindexes:
                        continue
                    item_name = item.get('item_name')

                    if item_name in bad_item_names:
                        continue
                    proper_name = item.get('proper_name')
                    item_slot = item.get('item_slot')
                    image_url = item.get('image_url')
                    image_url_large = item.get('image_url_large')
                    items_game_info = items_game['items'].get(str(defindex))
                    if 'prefab' in items_game_info:
                        for prefab in items_game_info['prefab'].split(" "):
                            prefab = items_game['prefabs'][prefab]
                            items_game_info = combine_dicts(items_game_info, prefab)

                    image_inventory = items_game_info.get('image_inventory')

                    if existing_item:
                        existing_item.equip_regions = []
                    equip_regions = []
                    equip_region = items_game_info.get('equip_region')
                    if equip_region:
                        if isinstance(equip_region, dict) is True:
                            equip_regions = equip_region
                            equip_region = []
                    if equip_region:
                        equip_regions.append(equip_region)
                    else:
                        equip_region_dict = items_game_info.get('equip_regions')
                        if equip_region_dict:
                            equip_regions += list_from_vdf_dict(equip_region_dict)
                        else:
                            for amend_region, region_defindexes in amend_equip_regions.items():
                                if defindex in region_defindexes:
                                    equip_regions.append(amend_region)

                    used_by_classes = item.get('used_by_classes')
                    model_player = items_game_info.get('model_player')
                    class_models = {}

                    if used_by_classes and len(used_by_classes) is 1:
                        if model_player:
                            class_models.update({used_by_classes[0].lower(): model_player})
                        else:
                            continue

                    elif not used_by_classes or len(used_by_classes) > 1:
                        if not used_by_classes:
                            used_by_classes = all_classes
                        model_player_per_class = items_game_info.get('model_player_per_class')
                        for tf2_class in used_by_classes:
                            tf2_class = tf2_class.lower()
                            if model_player_per_class:
                                class_model = model_player_per_class.get(tf2_class)
                            elif model_player:
                                #class_model = model_player
                                continue
                            else:
                                continue
                            class_and_model = {tf2_class: class_model}
                            class_models.update(class_and_model)

                    visuals = items_game_info.get('visuals')
                    if existing_item:
                        existing_item.bodygroups = []
                    bodygroups = []
                    if visuals:
                        bodygroups_dict = visuals.get('player_bodygroups')
                        if bodygroups_dict:
                            bodygroups += list_from_vdf_dict(bodygroups_dict)
                        if len(used_by_classes) is 1 and 'hat' in bodygroups:
                            if used_by_classes[0] in ('Pyro', 'Demoman', 'Heavy', 'Medic', 'Spy'):
                                bodygroups.remove('hat')  # These guys don't even have a hat to hide...
                        if 'disconnected_floating_item' in equip_regions:
                            bodygroups = []  # Disconnected items don't need to hide anything. What's wrong with you Volvo.

                    if existing_item:
                        print u"Updating item: {} ({})".format(item_name, defindex)
                        existing_item.defindex = defindex
                        existing_item.item_name = item_name
                        existing_item.proper_name = proper_name
                        existing_item.item_slot = item_slot
                        existing_item.image_url = image_url
                        existing_item.image_url_large = image_url_large
                        existing_item.image_inventory = image_inventory
                        for class_name in class_array:
                            class_models_c_m = class_models.get(class_name)
                            existing_c_m = existing_item.class_model.get(class_name)
                            if class_models_c_m and existing_c_m and existing_c_m.model_path != class_models[class_name]:
                                existing_c_m.model_path = class_models[class_name]
                            elif class_models_c_m and not existing_c_m:
                                model = class_models[class_name]
                                existing_item.class_model[class_name] = get_or_create(db.session, TF2ClassModel,
                                                                                      defindex=defindex,
                                                                                      class_name=class_name,
                                                                                      model_path=model)
                            elif existing_c_m and not class_models_c_m:
                                db.session.delete(existing_item.class_model[class_name])
                        for equip_region in equip_regions:
                            existing_item.equip_regions.append(get_or_create(db.session, TF2EquipRegion, equip_region=equip_region))
                        for bodygroup in bodygroups:
                            existing_item.bodygroups.append(get_or_create(db.session, TF2BodyGroup, bodygroup=bodygroup))
                        db.session.add(existing_item)
                    else:
                        print u"Adding item: {} ({})".format(item_name, defindex)
                        db_item = TF2Item(defindex, item_name, proper_name, item_slot, image_url, image_url_large,
                                          image_inventory, class_models, equip_regions, bodygroups)
                        db.session.add(db_item)
                    db.session.commit()
            print "All items processed."
            update_completed = True


def delete_expired_packages():
    packages = ModPackage.query.filter(ModPackage.expire_date <= datetime.datetime.utcnow())\
        .filter(ModPackage.deleted == False).all()
    print "{} packages to delete.".format(len(packages))
    for package in packages:
        package_path = os.path.abspath(os.path.join(current_app.config['OUTPUT_FOLDER_LOCATION'],
                                                    str(package.mod_id), package.filename))
        try:
            os.remove(package_path)
            print u"Deleted package where {} replaces {}.".format(package.mod.pretty_name, package.replacement.item_name)
        except OSError:
            print u"Package where {} replaces {} already deleted.".format(package.mod.pretty_name, package.replacement.item_name)
        package.deleted = True
        db.session.add(package)
        db.session.commit()


def update_authors_steam_info():
    authors = ModAuthor.query.group_by(ModAuthor.user_id).order_by(ModAuthor.user_id).all()
    print "Updating {} authors.".format(len(authors))
    profile_list = sorted(steam.user.profile_batch([author.user.steam_id for author in authors]), key=lambda x: x.id64)
    for i, profile in enumerate(profile_list):
        authors[i].user.update_steam_info(profile)
    db.session.commit()