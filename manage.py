"""
Manager script :)

Takes the following commands:
- runserver
- shell
- update_tf2_items (Updates information about TF2 Items stored in the DB - Runs every 14d via cron)
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
def update_authors_steam_info():
    from app.scripts.scripts import update_authors_steam_info as _update_authors_steam_info
    _update_authors_steam_info()


@manager.command
def cron_update():
    import datetime
    from app.filters import datetime_to_datestring
    start = datetime.datetime.utcnow()
    print "Performing complete cron update at: {}".format(datetime_to_datestring(start))
    print "--- Deleting expired packages ---"
    delete_expired_packages()
    print "--- Updating author Steam info ---"
    update_authors_steam_info()
    end = datetime.datetime.utcnow()
    elapsed = divmod((end-start).total_seconds(), 60)
    print "Finished complete cron update at: {}, took: {}m {}s".format(datetime_to_datestring(end), int(elapsed[0]), int(elapsed[1]))

if __name__ == "__main__":
    manager.run()