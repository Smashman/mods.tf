"""
Manager script :)

Takes the following commands:
- runserver
- shell
- update_tf2_items (Updates information about TF2 Items stored in the DB - Runs every 24h via cron)
- delete_expired_packages (Deletes packages that have expired - Runs every 24h via cron)
"""

from app import app
from flask.ext.script import Manager

manager = Manager(app)


@manager.command
def update_tf2_items():
    from app.scripts.scripts import update_tf2_items as _update_tf2_items
    _update_tf2_items()


@manager.command
def delete_expired_packages():
    from app.scripts.scripts import delete_expired_packages as _delete_expired_packages
    _delete_expired_packages()


@manager.command
def test():
    from app.mods.models import Mod
    from app.tf2.models import TF2Item
    from app.utils.utils import package_mod_to_item

    mod = Mod.query.get(12)
    replacement = TF2Item.query.get(260)
    package_mod_to_item(mod, replacement)

if __name__ == "__main__":
    manager.run()