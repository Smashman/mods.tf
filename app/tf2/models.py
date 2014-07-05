from app import db
from app.models import get_or_create


class TF2Class(db.Model):
    __tablename__ = "tf2_class"
    class_name = db.Column(db.String(64), primary_key=True, nullable=False)

    def __init__(self, class_name=None):
        self.class_name = class_name

    def __repr__(self):
        return self.full_name or self.class_name.capitalize()


class TF2ClassModel(db.Model):
    __tablename__ = "tf2_schema_classmodel"
    defindex = db.Column(db.Integer, db.ForeignKey('tf2_schema.defindex'), primary_key=True)
    class_name = db.Column(db.String(64), db.ForeignKey('tf2_class.class_name'), primary_key=True)
    model_path = db.Column(db.String(256))

    tf2_class = db.relationship("TF2Class", backref="item_model")

    def __init__(self, defindex=None, class_name=None, model_path=None):
        self.defindex = defindex
        self.class_name = class_name
        self.model_path = model_path

    def __repr__(self):
        return self.model_path


class TF2BodyGroup(db.Model):
    __tablename__ = "tf2_bodygroups"
    bodygroup = db.Column(db.String(64), primary_key=True, nullable=False)
    full_name = db.Column(db.String(128))

    def __init__(self, bodygroup=None, full_name=None):
        self.bodygroup = bodygroup
        self.full_name = full_name

    def __repr__(self):
        return self.full_name or self.bodygroup.capitalize()


schema_bodygroup = db.Table(
    "tf2_schema_bodygroup",
    db.Column('defindex', db.Integer, db.ForeignKey('tf2_schema.defindex')),
    db.Column('bodygroup', db.String(64), db.ForeignKey('tf2_bodygroups.bodygroup'))
)


class TF2EquipRegion(db.Model):
    __tablename__ = "tf2_equip_regions"
    equip_region = db.Column(db.String(64), primary_key=True, nullable=False)
    full_name = db.Column(db.String(128))

    def __init__(self, equip_region=None, full_name=None):
        self.equip_region = equip_region
        self.full_name = full_name

    def __repr__(self):
        return self.full_name or self.equip_region.capitalize()


schema_equipregion = db.Table(
    "tf2_schema_equipregion",
    db.Column('defindex', db.Integer, db.ForeignKey('tf2_schema.defindex')),
    db.Column('equip_region', db.String(64), db.ForeignKey('tf2_equip_regions.equip_region'))
)


class TF2Item(db.Model):
    __tablename__ = "tf2_schema"
    defindex = db.Column(db.Integer, primary_key=True, autoincrement=False)
    item_name = db.Column(db.String(256, collation="utf8_swedish_ci"))
    proper_name = db.Column(db.Boolean)
    item_slot = db.Column(db.String(64))
    image_url = db.Column(db.String(256))
    image_url_large = db.Column(db.String(256))

    # Relationships
    equip_regions = db.relationship('TF2EquipRegion', secondary=schema_equipregion, backref=db.backref('tf2_item',
                                                                                                       lazy="dynamic"),
                                    lazy="joined")
    bodygroups = db.relationship('TF2BodyGroup', secondary=schema_bodygroup, backref=db.backref('tf2_item',
                                                                                                lazy="dynamic"),
                                 lazy="joined")
    class_model = db.relationship('TF2ClassModel', backref=db.backref('tf2_item'),
                                  lazy="joined", cascade='all')

    __mapper_args__ = {
        "order_by": [db.asc(defindex)]
    }

    def __repr__(self):
        return "{} (defindex: {})".format(self.item_name, self.defindex)

    def __init__(self, defindex=None, item_name=None, proper_name=None, item_slot=None, image_url=None,
                 image_url_large=None, class_model=None, _equip_regions=None, _bodygroups=None):
        self.defindex = defindex
        self.item_name = item_name
        self.proper_name = proper_name
        self.item_slot = item_slot
        self.image_url = image_url
        self.image_url_large = image_url_large
        if class_model:
            for class_name, model in class_model.items():
                self.class_model.append(get_or_create(db.session, TF2ClassModel, defindex=defindex,
                                                      class_name=class_name, model_path=model))
        if _equip_regions:
            for equip_region in _equip_regions:
                self.equip_regions.append(get_or_create(db.session, TF2EquipRegion, equip_region=equip_region))
        if _bodygroups:
            for bodygroup in _bodygroups:
                self.bodygroups.append(get_or_create(db.session, TF2BodyGroup, bodygroup=bodygroup))