import steam
import urllib2
from steam.api import HTTPError
from .. import db
from ..models import get_or_create
from ..tf2.models import TF2Item, TF2Class

all_classes = [u'Scout', u'Soldier', u'Pyro', u'Demoman', u'Heavy', u'Engineer', u'Sniper', u'Medic', u'Spy']


def list_from_vdf_dict(dictionary):
    return_list = []
    for dict_item, number in dictionary.items():
        if number is not None and number > 0:
            return_list.append(dict_item)
    return return_list


def insert_classes():
    for tf2_class in all_classes:
        get_or_create(db.session, TF2Class, class_name=tf2_class.lower())
    db.session.commit()


def update_tf2_items():
    update_completed = False

    insert_classes()

    bad_item_types = ["CheatDetector", "Tournament Medal", "Cursed Soul"]
    bad_item_names = ["TF_GateBot_Light"]
    bad_defindexes = [5606,  # Damaged Capacitor (Not equippable)
                      8938,  # Glitched Circuit Board (Not equippable)
                      30143, 30144, 30145, 30146, 30147, 30148, 30149, 30150, 30151, 30152, 30153, 30154, 30155, 30156,
                      30157, 30158, 30159, 30160, 30161]
    amend_equip_regions = {"hat": [162, 711, 712, 713], "belt_misc": [1011], "ring": [5075], "shirt": [1088]}

    for i in range(10):
        if not update_completed:
            try:
                schema = steam.api.interface("IEconItems_440").GetSchema(language="english").get("result")
                items_game_url = schema.get('items_game_url')
                items_game = steam.vdf.load(urllib2.urlopen(items_game_url)).get('items_game')
            except HTTPError:
                db.session.rollback()
                continue

            for item in schema['items']:
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
                            items_game_info.update(items_game['prefabs'][prefab])

                    equip_regions = []
                    equip_region = items_game_info.get('equip_region')
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

                    visuals = items_game_info.get('visuals')
                    bodygroups = []
                    if visuals:
                        bodygroups_dict = visuals.get('player_bodygroups')
                        if bodygroups_dict:
                            bodygroups += list_from_vdf_dict(bodygroups_dict)

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
                                class_model = model_player
                            else:
                                continue
                            class_and_model = {tf2_class: class_model}
                            class_models.update(class_and_model)
                    if existing_item:
                        db.session.delete(existing_item)
                    print u"Adding item: {} ({})".format(item_name, defindex)
                    db_item = TF2Item(defindex, item_name, proper_name, item_slot, image_url, image_url_large,
                                      class_models, equip_regions, bodygroups)
                    db.session.add(db_item)
                    db.session.commit()
            print "All items inserted."
            update_completed = True