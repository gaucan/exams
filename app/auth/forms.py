from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,validators
from wtforms.validators import Required

#pouzite na login
class LoginForm(Form):
	login = TextField('login', validators = [Required()])
	password = PasswordField('password', validators = [Required()])
    