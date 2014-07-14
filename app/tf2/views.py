from flask import url_for, Response, abort, Blueprint, request
from models import TF2Item, TF2ClassModel, TF2BodyGroup, TF2EquipRegion
from flask.ext.login import login_required
from sqlalchemy import func
import json
from .. import db

tf2 = Blueprint("tf2", __name__, url_prefix="/tf2")


@tf2.route('/api/', methods=['POST'])
@login_required
def api():
    form_values = request.form
    item_name = form_values.get("search_data[item_name]")
    class_name = form_values.get("search_data[class_name]")
    bodygroup = form_values.get("search_data[bodygroup]")
    equip_region = form_values.get("search_data[equip_region]")
    mod_id = form_values.get("mod_id")
    page = request.form.get('page')
    wildcards = ["%", "_"]
    if request.method != 'POST' or any([w in item_name for w in wildcards]):
        abort(404)
    items_query = TF2Item.query.filter(TF2Item.item_name.contains(item_name))
    if class_name == "all_class":
        sq = db.session.query(TF2ClassModel.defindex, func.count(TF2ClassModel).label("class_count")).group_by(TF2ClassModel.defindex).subquery()
        items_query = items_query.join(sq, TF2Item.defindex == sq.c.defindex).filter(sq.c.class_count == 9)
    else:
        items_query = items_query.filter(~TF2Item.class_model.any(TF2ClassModel.class_name != class_name))
    if bodygroup != "0":
        items_query = items_query.filter(TF2Item.bodygroups.any(TF2BodyGroup.bodygroup == bodygroup))
    if equip_region != "0":
        items_query = items_query.filter(TF2Item.equip_regions.any(TF2EquipRegion.equip_region == equip_region))
    items_query = items_query.paginate(int(page), per_page=20)
    items = []
    for item in items_query.items:
        items.append(u"<a class=\"test\" href=\"{url}\" title=\"{item.item_name}\"><img src=\"{item.image_url}\" /></a>".format(item=item, url=url_for('mods.package_mod', mod_id=mod_id, defindex=item.defindex)))
    if items_query.has_next:
        items.append(u"<div class=\"next\"><img src=\"http://media.steampowered.com/apps/440/icons/wikicap.cd511140da7a50a2a9cf9f83bd58a12e4652d5ca.png\" /></div>")
    if items_query.has_prev:
        items.insert(0, u"<div class=\"prev\"><img src=\"http://media.steampowered.com/apps/440/icons/wikicap.cd511140da7a50a2a9cf9f83bd58a12e4652d5ca.png\" /></div>")
    items_dict = {"items": items}
    return Response(json.dumps(items_dict),  mimetype='application/json')