from flask import url_for, Response, abort, Blueprint, request, render_template
from models import TF2Item, TF2ClassModel, TF2BodyGroup, TF2EquipRegion, schema_bodygroup
from ..mods.models import Mod, PackageDownload, ModPackage
from flask.ext.login import login_required
from sqlalchemy import func, or_, and_
import json
from .. import db
from sqlalchemy import desc

tf2 = Blueprint("tf2", __name__, url_prefix="/tf2")


def item_search(classes=None, bodygroups=None, equip_regions=None, item_name=None):
    items_query = TF2Item.query.filter_by(inactive=False)
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
            items_query = items_query.filter(sq.c.class_count > 1).filter(sq.c.class_count < 9)
        elif len(classes) == 1:
            items_query = items_query.filter(sq.c.class_count == 1)
    else:
        return
    if equip_regions:
        items_query = items_query.filter(TF2Item.equip_regions.any(or_(*[TF2EquipRegion.equip_region == equip_region for equip_region in equip_regions])))
    if bodygroups:
        items_query = items_query.filter(TF2Item.bodygroups.any(or_(*[TF2BodyGroup.bodygroup == bodygroup for bodygroup in bodygroups])))
        bodygroup_count = db.session.query(schema_bodygroup.c.defindex, func.count('*').label("bg_count")).group_by(schema_bodygroup.c.defindex).subquery()
        items_query = items_query.join(bodygroup_count, TF2Item.defindex == bodygroup_count.c.defindex).filter(bodygroup_count.c.bg_count == len(bodygroups))
    else:
        items_query = items_query.filter(TF2Item.bodygroups == None)
    return items_query


def format_query(items_query, mod_id, page):
    mod = Mod.query.get_or_404(mod_id)
    authors = set(user.account_id for user in mod.authors)
    if items_query and items_query.count() > 0:
        count = items_query.count()
        items_query = items_query.paginate(int(page), per_page=36)
        for item in items_query.items:
            item.downloads = PackageDownload.query.join(ModPackage).join(TF2Item).filter(TF2Item.defindex == item.defindex) \
                .filter(ModPackage.mod_id == mod_id).filter(~PackageDownload.user_id.in_(authors)).count()
    else:
        return {"err_msg": "No items found matching these criteria.", "count": 0}

    items = render_template('tf2/api_result.html', items=items_query, mod_id=mod_id)
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
    page = form_values.get('page')
    if len(classes) < 1:
        return Response(json.dumps({"err_msg": "No classes selected, please select a class to search.", "count": 0}),  mimetype='application/json')
    if not page.isnumeric():
        return Response(json.dumps({"err_msg": "Error, please refresh the page and try again.", "count": 0}),  mimetype='application/json')

    items_query = item_search(classes, bodygroups, equip_regions, item_name)
    items_dict = format_query(items_query, mod_id, page)

    if "err_msg" in items_dict:
        return Response(json.dumps({"err_msg": items_dict.get('err_msg')}),  mimetype='application/json')

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
    if len(classes) < 1:
        return Response(json.dumps({"err_msg": "No classes selected, please select a class to search.", "count": 0}),  mimetype='application/json')
    if not page.isnumeric():
        return Response(json.dumps({"err_msg": "Error, please refresh the page and try again.", "count": 0}),  mimetype='application/json')

    items_query = item_search(classes, bodygroups, equip_regions, item_name)
    items_dict = {"count": items_query.count()}

    return Response(json.dumps(items_dict),  mimetype='application/json')


@tf2.route('/items/')
def item_download_counts():
    sq = db.session.query(ModPackage.defindex, func.count(PackageDownload).label("download_count"))\
        .join(PackageDownload).group_by(ModPackage.defindex).subquery()
    top_100_downloaded = db.session.query(TF2Item, "download_count").join(sq, TF2Item.defindex == sq.c.defindex)\
        .order_by(desc("download_count")).limit(100).all()
    return render_template('tf2/top_100_downloads.html', items=top_100_downloaded, title="Top {} replaced items".format(len(top_100_downloaded)))