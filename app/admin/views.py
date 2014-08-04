from flask.ext.login import current_user
from flask.ext.admin import Admin, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from ..users.models import User
from ..mods.models import Mod, ModPackage, PackageDownload


class Auth(object):
    def is_accessible(self):
        return current_user.is_admin()


class AdminModelView(Auth, ModelView):
    """ Used for setting up admin-only model views """
    pass


class AdminIndex(Auth, AdminIndexView):
    @expose('/')
    def index(self):
        stats = {
            "users": User.query.count(),
            "mods": Mod.query.count(),
            "packages": ModPackage.query.count(),
            "downloads": PackageDownload.query.count()
        }
        return self.render('admin/index.html', stats=stats)


class UserView(Auth, ModelView):
    column_searchable_list = ('name', User.name)

admin = Admin(name="mods.tf", index_view=AdminIndex())