from flask import url_for, Response, abort, Blueprint, request
from models import TF2Item
from flask.ext.login import login_required
import json

tf2 = Blueprint("tf2", __name__, url_prefix="/tf2")


@tf2.route('/api/', methods=['POST'])
@login_required
def api():
    item_name = request.form.get('item_name')
    page = request.form.get('page')
    wildcards = ["%", "_"]
    if request.method != 'POST' or any([w in item_name for w in wildcards]) or len(item_name) < 3:
        abort(404)
    items_query = TF2Item.query.filter(TF2Item.item_name.like("%"+item_name+"%")).paginate(int(page), per_page=20)
    #beards_query = TF2Item.query.filter(~TF2Item.class_model.any(TF2ClassModel.class_name!=class_name))\
        #.filter(TF2Item.equip_regions.any(equip_region='beard')).all()
    items = []
    for item in items_query.items:
        items.append(u"<a class=\"test\" href=\"{url}\" title=\"{item.item_name}\"><img src=\"{item.image_url}\" /></a>".format(item=item, url=url_for('mods.package_mod', mod_id=2, defindex=item.defindex)))
    if items_query.has_next:
        items.append(u"<div class=\"next\"><img src=\"http://media.steampowered.com/apps/440/icons/wikicap.cd511140da7a50a2a9cf9f83bd58a12e4652d5ca.png\" /></div>")
    items_dict = {"items": items}
    return Response(json.dumps(items_dict),  mimetype='application/json')