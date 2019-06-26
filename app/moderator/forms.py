from flask.ext.wtf import Form
from wtforms import BooleanField, IntegerField, SubmitField
from wtforms.validators import NumberRange
from flask.ext.wtf.html5 import NumberInput


class TokenGrant(Form):
    token_number = IntegerField('Tokens:', widget=NumberInput(), validators=[NumberRange(min=-1, max=10)])
    is_moderator = BooleanField('Is user a moderator:')
    save = SubmitField("Save")