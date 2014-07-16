from flask.ext.wtf import Form
from wtforms import TextField, SelectMultipleField
from wtforms import widgets

class ItemSearch(Form):
    item_name = TextField('Item name:')
    classes = SelectMultipleField('Class:')
    equip_regions = SelectMultipleField('Equip region:')
    bodygroups = SelectMultipleField('Bodygroup:')