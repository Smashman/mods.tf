from flask.ext.login import current_user
from flask.ext.admin import Admin, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from jinja2 import Markup
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
        from collections import OrderedDict
        import datetime
        stats = {
            "users": User.query.filter_by(enabled=True).count(),
            "mods": Mod.query.filter_by(visibility="Pu").count(),
            "hidden mods": Mod.query.filter_by(visibility="H").count(),
            "current packages": ModPackage.query.filter(ModPackage.expire_date > datetime.datetime.utcnow()).count(),
            "expired packages": ModPackage.query.filter(ModPackage.expire_date < datetime.datetime.utcnow()).count(),
            "downloads": PackageDownload.query.count()
        }
        stats = OrderedDict(sorted(stats.items(), key=lambda t: t[0]))
        return self.render('admin/index.html', stats=stats)


class UserView(Auth, ModelView):
    def show_avatar(self, context, model, name):
        if not model.avatar_medium:
            return ''
        return Markup('<img src="{}">'.format(model.avatar_medium))

    def profile_url(self, context, model, name):
        if not model.profile_url:
            return ''
        return Markup('<a href="{0}" target="_blank">{0}</a>'.format(model.profile_url))

    column_display_pk = True
    column_exclude_list = ['avatar_small', 'avatar_large']
    column_formatters = {
        'avatar_medium': show_avatar,
        'profile_url': profile_url
    }
    column_searchable_list = ['name']

admin = Admin(name="mods.tf", index_view=AdminIndex())