from flask.ext.login import current_user
from flask.ext.admin import Admin, expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView
from jinja2 import Markup
from app import db
from ..users.models import User
from ..mods.models import Mod, ModPackage, PackageDownload, ModAuthor
from datetime import datetime, timedelta


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
        stats = OrderedDict([
            ("users", User.query.filter_by(enabled=True).count(),),
            ("downloads", PackageDownload.query.count()),
            ("mods", Mod.query.filter_by(visibility="Pu").count(),),
            ("hidden mods", Mod.query.filter_by(visibility="H").count(),),
            ("valid packages", ModPackage.query.filter(ModPackage.expire_date > datetime.datetime.utcnow()).count(),),
            ("expired packages - not deleted", ModPackage.query.filter(ModPackage.expire_date < datetime.datetime.utcnow()).filter(ModPackage.deleted == False).count(),)
        ])
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
    form_excluded_columns = ['mod', 'author']
    column_formatters = {
        'avatar_medium': show_avatar,
        'profile_url': profile_url
    }
    column_searchable_list = ['name']
    form_ajax_refs = {
        'download': {
            'fields': (PackageDownload.package_id,),
            'page_size': 10
        }
    }


class BigDownloaders(Auth, BaseView):
    """ Views for database-stored site logs. """

    @staticmethod
    def user_download_count(hours=None):
        rows = db.session.query(PackageDownload, db.func.count(PackageDownload.id))
        if hours:
            _time_ago = datetime.utcnow() - timedelta(hours=hours)
            rows = rows.filter(PackageDownload.downloaded >= _time_ago)
        rows = rows.group_by(PackageDownload.user_id).\
            order_by(db.func.count(PackageDownload.package_id).desc()).\
            limit(30).\
            all()
        return rows

    @expose('/')
    def index(self):
        """ Renders a list of users who have done an lot of downloads in particular time frames. """

        return self.render(
            'admin/big_downloaders.html',
            daily_downloaders=self.user_download_count(24),
            weekly_downloaders=self.user_download_count(24 * 7),
            monthly_downloaders=self.user_download_count(24 * 7 * 30),
            all_time_downloaders=self.user_download_count()
        )

admin = Admin(name="mods.tf", index_view=AdminIndex())
admin.add_view(BigDownloaders(name="Big downloaders", category="Reports"))