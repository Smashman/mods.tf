from app import db
from app.models import get_or_create
import datetime

mod_author = db.Table(
    "mod_author",
    db.Column('mod_id', db.Integer, db.ForeignKey('mods.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.account_id'))
)

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
    zip_file = db.Column(db.String(256))
    workshop_id = db.Column(db.Integer)
    package_format = db.Column(db.Enum('VPK', 'ZIP', name='package_types'), default='VPK')
    split_class = db.Column(db.Boolean, default=True)
    license = db.Column(db.String(16))  # Ought to be Enum.
    manifest_steamid = db.Column(db.Integer)
    item_slot = db.Column(db.String(64))
    image_inventory = db.Column(db.String(256))
    uploaded = db.Column(db.DateTime, default=datetime.datetime.now)
    visibility = db.Column(db.Enum('H', 'Pu', 'Pr', name='visibility_types'), default='H')  # Hidden, Public, Private
    enabled = db.Column(db.Boolean, default=True)

    authors = db.relationship('User', secondary=mod_author, backref=db.backref('mod',
                                                                               lazy="dynamic"), lazy="joined")

    equip_regions = db.relationship('TF2EquipRegion', secondary=mod_equipregion, backref=db.backref('mod',
                                                                                                    lazy="dynamic"),
                                    lazy="joined")
    bodygroups = db.relationship('TF2BodyGroup', secondary=mod_bodygroup, backref=db.backref('mod',
                                                                                             lazy="dynamic"),
                                 lazy="joined")
    class_model = db.relationship('ModClassModel', backref=db.backref('mod'),
                                  lazy="joined", cascade='all')

    __mapper_args__ = {
        "order_by": [db.asc(id)]
    }

    def __repr__(self):
        return "{} (id: {})".format(self.pretty_name, self.id)

    def __init__(self, zip_file=None, author=None):
        self.zip_file = zip_file
        self.authors.append(author)