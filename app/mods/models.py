from app import db
import datetime
from sqlalchemy.orm.collections import attribute_mapped_collection

mod_author = db.Table(
    "mod_author",
    db.Column('mod_id', db.Integer, db.ForeignKey('mods.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.account_id'))
)


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
        return "{} ({})".format(self.class_name, self.mod_id)


class ModPackage(db.Model):
    __tablename__ = "mod_package"
    id = db.Column(db.Integer, primary_key=True)
    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'), nullable=False)
    defindex = db.Column(db.Integer, db.ForeignKey('tf2_schema.defindex'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    expire_date = db.Column(db.DateTime, default=datetime.datetime.utcnow() + datetime.timedelta(days=2), nullable=False)

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
        return "{} replacing {}".format(self.mod_id, self.defindex)


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
        return "Download record for package: {} -> {} by user: {}".format(self.package.mod.pretty_name,
                                                                          self.package.replacement.item_name,
                                                                          self.user.name)

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
    license = db.Column(db.String(16))  # Ought to be Enum.
    manifest_steamid = db.Column(db.Integer)
    item_slot = db.Column(db.String(64))
    image_inventory = db.Column(db.String(256))
    uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    visibility = db.Column(db.Enum('H', 'Pu', 'Pr', name='visibility_types'), default='H')  # Hidden, Public, Private
    enabled = db.Column(db.Boolean, default=True)

    authors = db.relationship('User', secondary=mod_author, backref=db.backref('mod',
                                                                               lazy="dynamic"), lazy="subquery")

    equip_regions = db.relationship('TF2EquipRegion', secondary=mod_equipregion, backref=db.backref('mod',
                                                                                                    lazy="dynamic"),
                                    lazy="subquery")
    bodygroups = db.relationship('TF2BodyGroup', secondary=mod_bodygroup, backref=db.backref('mod',
                                                                                             lazy="dynamic"),
                                 lazy="subquery")
    class_model = db.relationship('ModClassModel', backref=db.backref('mod'),
                                  collection_class=attribute_mapped_collection('class_name'),
                                  lazy="subquery", cascade='all')

    __mapper_args__ = {
        "order_by": [db.asc(uploaded)]
    }

    def __repr__(self):
        return "{} (id: {})".format(self.pretty_name, self.id)

    def __init__(self, zip_file=None, author=None):
        self.zip_file = zip_file
        self.authors.append(author)