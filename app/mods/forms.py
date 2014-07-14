from flask.ext.wtf import Form
from wtforms import TextField, SelectField
from wtforms.validators import Required

class ItemSearch(Form):
    item_name = TextField('Item name:', validators=[Required()])
    class_name = SelectField('Class:')
    equip_region = SelectField('Equip region:')
    bodygroup = SelectField('Bodygroup:')