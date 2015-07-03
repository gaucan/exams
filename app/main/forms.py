# coding=utf-8

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,SelectField,validators,FieldList, TextAreaField
from wtforms.validators import Required

class FeedbackForm(Form):
    comment = TextAreaField(u'Správa:', validators=[validators.required()])

