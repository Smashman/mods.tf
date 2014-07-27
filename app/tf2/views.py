from flask import url_for, Response, abort, Blueprint, request, render_template
from models import TF2Item, TF2ClassModel, TF2BodyGroup, TF2EquipRegion
from ..mods.models import Mod, PackageDownload, ModPackage
from flask.ext.login import login_required
from sqlalchemy import func
import json
from .. import db

tf2 = Blueprint("tf2", __name__, url_prefix="/tf2")


def item_search(classes=None, bodygroups=None, equip_regions=None, item_name=None):
    items_query = TF2Item.query
    wildcards = ["%", "_"]
    if item_name:
        if any([w in item_name for w in wildcards]):
            return
        items_query = items_query.filter(TF2Item.item_name.contains(item_name))
    if len(classes) > 0:
        for class_name in classes:
            items_query = items_query.filter(TF2Item.class_model.any(TF2ClassModel.class_name == class_name))
        sq = db.session.query(TF2ClassModel.defindex, func.count(TF2ClassModel).label("class_count")).group_by(TF2ClassModel.defindex).subquery()
        items_query = items_query.join(sq, TF2Item.defindex == sq.c.defindex)
        if len(classes) == 9:
            pass
        elif len(classes) > 1:
            items_query = items_query.filter(sq.c.class_count == 9)
        else:
            items_query = items_query.filter(sq.c.class_count == 1)
    else:
        return
    if bodygroups:
        for bodygroup in bodygroups:
            if bodygroup != "0":
                items_query = items_query.filter(TF2Item.bodygroups.any(TF2BodyGroup.bodygroup == bodygroup))
    if equip_regions:
        for equip_region in equip_regions:
            if equip_region != "0":
                items_query = items_query.filter(TF2Item.equip_regions.any(TF2EquipRegion.equip_region == equip_region))
    return items_query


def format_query(items_query, mod_id, page):
    mod = Mod.query.get_or_404(mod_id)
    count = items_query.count()
    items_query = items_query.paginate(int(page), per_page=36)
    if count < 1:
        return {"status": "No items found matching these criteria.", "count": 0}
    for item in items_query.items:
        item.downloads = PackageDownload.query.join(ModPackage).join(TF2Item).filter(TF2Item.defindex == item.defindex).count()

    items = render_template('tf2/items.html', items=items_query, mod_id=mod_id)
    return {"items": items, "count": count}


@tf2.route('/api/', methods=['POST'])
@login_required
def api():
    form_values = request.form
    item_name = form_values.get("search_data[item_name]")
    classes = form_values.getlist("search_data[classes][]")
    bodygroups = form_values.getlist("search_data[bodygroups][]")
    equip_regions = form_values.getlist("search_data[equip_regions][]")
    mod_id = form_values.get("mod_id")
    page = request.form.get('page')
    print page
    if len(classes) < 1:
        return Response(json.dumps({"status": "No classes selected, please select a class to search.", "count": 0}),  mimetype='application/json')
    if not page.isnumeric():
        return Response(json.dumps({"status": "Error, please refresh the page and try again.", "count": 0}),  mimetype='application/json')

    items_query = item_search(classes, bodygroups, equip_regions, item_name)
    items_dict = format_query(items_query, mod_id, page)

    if "status" in items_dict:
        return Response(json.dumps({"status": items_dict.get('status')}),  mimetype='application/json')

    return Response(json.dumps(items_dict),  mimetype='application/json')

@tf2.route('/api/count/', methods=['POST'])
@login_required
def api_count():
    form_values = request.form
    item_name = form_values.get("search_data[item_name]")
    classes = form_values.getlist("search_data[classes][]")
    bodygroups = form_values.getlist("search_data[bodygroups][]")
    equip_regions = form_values.getlist("search_data[equip_regions][]")
    page = request.form.get('page')
    print page
    if len(classes) < 1:
        return Response(json.dumps({"status": "No classes selected, please select a class to search.", "count": 0}),  mimetype='application/json')
    if not page.isnumeric():
        return Response(json.dumps({"status": "Error, please refresh the page and try again.", "count": 0}),  mimetype='application/json')

    items_query = item_search(classes, bodygroups, equip_regions, item_name)
    items_dict = {"count": items_query.count()}

    return Response(json.dumps(items_dict),  mimetype='application/json')