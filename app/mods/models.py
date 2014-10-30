from app import db
import datetime
from sqlalchemy.orm.collections import attribute_mapped_collection


class ModAuthor(db.Model):
    __tablename__ = "mod_author"
    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.account_id'), primary_key=True)
    order = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship("User", backref="author")
    mod = db.relationship("Mod", backref="author")

    __mapper_args__ = {
        "order_by": [db.asc(order)]
    }

    def __repr__(self):
        return u"{user.name} is an author of mod {mod.pretty_name}".format(user=self.user, mod=self.mod)


class ModImage(db.Model):
    __tablename__ = "mod_image"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'), nullable=False)
    uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    type = db.Column(db.Integer, default=0)

    def __init__(self, filename=None, mod_id=None, _type=None):
        self.filename = filename
        self.mod_id = mod_id
        self.type = _type


class ModClassModel(db.Model):
    __tablename__ = "mod_classmodel"
    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'), primary_key=True)
    class_name = db.Column(db.String(64), db.ForeignKey('tf2_class.class_name'), primary_key=True)
    model_path = db.Column(db.String(256))

    tf2_class = db.relationship("TF2Class", backref="mod_model")

    def __init__(self, mod_id=None, class_name=None, model_path=None):
        self.mod_id = mod_id
        self.class_name = class_name
        self.model_path = model_path

    def __repr__(self):
        return self.model_path


class ModPackage(db.Model):
    __tablename__ = "mod_package"
    id = db.Column(db.Integer, primary_key=True)
    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'), nullable=False)
    defindex = db.Column(db.Integer, db.ForeignKey('tf2_schema.defindex'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    expire_date = db.Column(db.DateTime, default=datetime.datetime.utcnow() + datetime.timedelta(days=2), nullable=False)
    deleted = db.Column(db.Boolean, default=False)

    mod = db.relationship("Mod", backref="package")
    replacement = db.relationship("TF2Item", backref="package")

    def __init__(self, mod_id=None, defindex=None, filename=None, long_date=False):
        self.mod_id = mod_id
        self.defindex = defindex
        self.filename = filename
        if long_date:
            self.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)

    def update_expire(self, long_date=False):
        if long_date:
            self.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        else:
            self.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=2)

    def __repr__(self):
        return u"{} replacing {}".format(self.mod_id, self.defindex)


class PackageDownload(db.Model):
    __tablename__ = "package_download"
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('mod_package.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.account_id'))
    downloaded = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="download")
    package = db.relationship("ModPackage", backref="download")

    def __init__(self, package_id=None, user_id=None):
        self.package_id = package_id
        self.user_id = user_id

    def __repr__(self):
        return u"Download record for package: {}".format(self.package_id)

mod_bodygroup = db.Table(
    "mod_bodygroup",
    db.Column('mod_id', db.Integer, db.ForeignKey('mods.id')),
    db.Column('bodygroup', db.String(64), db.ForeignKey('tf2_bodygroups.bodygroup'))
)

mod_equipregion = db.Table(
    "mod_equipregion",
    db.Column('mod_id', db.Integer, db.ForeignKey('mods.id')),
    db.Column('equip_region', db.String(64), db.ForeignKey('tf2_equip_regions.equip_region'))
)


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.String(64), primary_key=True)
    bg_num = db.Column(db.Integer)
    css = db.Column(db.Boolean)

    def __repr__(self):
        return self.id.capitalize()

mod_tag = db.Table(
    "mod_tag",
    db.Column('mod_id', db.Integer, db.ForeignKey('mods.id')),
    db.Column('tag', db.String(64), db.ForeignKey('tags.id'))
)


class Mod(db.Model):
    __tablename__ = "mods"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256))
    pretty_name = db.Column(db.String(256))
    description = db.Column(db.Text())
    zip_file = db.Column(db.String(256))
    workshop_id = db.Column(db.Integer)
    app = db.Column(db.Integer, default=440)
    package_format = db.Column(db.Enum('VPK', 'ZIP', name='package_types'), default='VPK')
    manifest_steamid = db.Column(db.Integer)
    item_slot = db.Column(db.String(64))
    image_inventory = db.Column(db.String(256))
    defindex = db.Column(db.Integer, nullable=True)
    hide_downloads = db.Column(db.Boolean, default=False)
    uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    visibility = db.Column(db.Enum('H', 'Pu', 'Pr', name='visibility_types'), default='H')  # Hidden, Public, Unlisted
    completed = db.Column(db.Boolean, default=False, nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    authors = db.relationship('User', secondary="mod_author", backref=db.backref('mod',
                                                                                 lazy="dynamic"), lazy="subquery",
                              order_by="ModAuthor.order")

    equip_regions = db.relationship('TF2EquipRegion', secondary=mod_equipregion, backref=db.backref('mod',
                                                                                                    lazy="dynamic"),
                                    lazy="subquery")
    bodygroups = db.relationship('TF2BodyGroup', secondary=mod_bodygroup, backref=db.backref('mod',
                                                                                             lazy="dynamic"),
                                 lazy="subquery")
    tags = db.relationship('Tag', secondary=mod_tag, backref=db.backref('mod',
                                                                        lazy="dynamic"),
                           lazy="subquery")
    class_model = db.relationship('ModClassModel', backref=db.backref('mod'),
                                  collection_class=attribute_mapped_collection('class_name'),
                                  lazy="subquery", cascade='all')

    __mapper_args__ = {
        "order_by": [db.desc(uploaded)]
    }

    def __repr__(self):
        return u"{} (id: {})".format(self.pretty_name, self.id)

    def __init__(self, zip_file=None, author=None):
        self.zip_file = zip_file
        self.authors.append(author)