from flask import abort
from flask.ext.login import current_user
from ..mods.models import PackageDownload, ModPackage, Mod
from ..tf2.views import item_search


def check_mod_permissions(mod):
    if mod.completed is False or mod.enabled is False:
        abort(404)
    elif mod.visibility == "H" and current_user not in mod.authors and not current_user.is_admin():
        abort(403)


def check_edit_permissions(mod):
    check_mod_permissions(mod)
    if current_user not in mod.authors and not current_user.is_admin():
        abort(403)


enabled_mods = lambda: Mod.query.filter_by(visibility="Pu", completed=True, enabled=True)


def get_mod_stats(mod, full_stats=False):
    item_query = item_search(
        classes=[_class for _class in mod.class_model],
        bodygroups=[bodygroup.bodygroup for bodygroup in mod.bodygroups],
        equip_regions=[equip_region.equip_region for equip_region in mod.equip_regions]
    )
    authors = set(user.account_id for user in mod.authors)
    downloads = PackageDownload.query.outerjoin(ModPackage).filter_by(mod_id=mod.id)\
        .filter(~PackageDownload.user_id.in_(authors))\
        .count()
    replacements = item_query.count()
    if full_stats:
        stats = {
            "downloads": downloads,
            "author_downloads": PackageDownload.query.outerjoin(ModPackage).filter_by(mod_id=mod.id)
            .filter(PackageDownload.user_id.in_(authors))
            .count(),
            "replacements": replacements,
            "item_query": item_query
        }
        return stats
    else:
        mod.downloads = downloads
        mod.replacements = replacements
        return mod