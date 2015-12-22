from flask.ext.wtf import Form
from wtforms import TextField, SelectField, TextAreaField


class Promo(Form):
    promo = SelectField('PromoID:')
    profile_urls = TextAreaField('Profile URLs:')

class CreateUser(Form):
    profile_url = TextField('Profile URL:')