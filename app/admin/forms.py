from flask.ext.wtf import Form
from wtforms import TextField, SelectField


class Promo(Form):
    promo = SelectField('PromoID:')
    user = TextField('User:')

class CreateUser(Form):
    profile_url = TextField('Profile URL:')