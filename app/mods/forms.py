from flask.ext.wtf import Form
from wtforms import TextField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import Required, Length


class ItemSearch(Form):
    item_name = TextField('Item name:')
    classes = SelectMultipleField('Class:')
    equip_regions = SelectMultipleField('Equip region:')
    bodygroups = SelectMultipleField('Bodygroup:')


class EditMod(Form):
    pretty_name = TextField('Pretty name:', validators=[Required()])
    workshop_id = TextField('Workshop ID:')
    package_format = SelectField("Package format:", validators=[Required()])
    #license = SelectField("License:")
    equip_regions = SelectMultipleField("Equip regions:")
    bodygroups = SelectMultipleField("Bodygroups:")
    publish = SubmitField("Save and Publish!")
    hide = SubmitField("Save and hide mod")