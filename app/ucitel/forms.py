from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,SelectField,validators,FieldList
from wtforms.validators import Required
from app.models import Miestnost
from app import db



#pouzite na tvorbu terminu
class TerminForm(Form):
	#DateField Text field that accepts a datetime.date value in a given format
	#DateTimeField Text field that accepts a datetime.datetime value in a given format
	# miestnost = TextField('miestnost', validators = [Required()])
	zaciatok_skusky_datum = TextField('zaciatok_skusky_datum', validators = [Required()])
	zaciatok_skusky_cas= TextField('zaciatok_skusky_cas', validators = [Required()])
	uzavierka_prihlasovania_datum = TextField('uzavierka_prihlasovania_datum', validators = [Required()])
	uzavierka_prihlasovania_cas = TextField('uzavierka_prihlasovania_cas', validators = [Required()])
	kapacita = TextField('kapacita', validators = [Required()])
	poznamka = TextField('poznamka')
	miestnost = SelectField('miestnost',
                validators=[validators.optional()],
                )




"""
#pouzite na updatovanie jednej znamky 
class ResultForm(Form):
	f1 = SelectField(u'f1',
                validators=[validators.optional()],
                choices=[('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D'),('E', 'E'),('FX', 'FX'),('n/a', 'n/a')])

#pouzite na updatovanie znamok zo skusky
class MultiResultForm(Form):
    selects = FieldList(SelectField(u'Select', 
                                    validators=[validators.optional()],
                                    choices=[('A', 'A'), ('B', 'B'), ('C', 'C'),
                                             ('D', 'D'), ('E', 'E'), ('FX', 'FX'),
                                             ('n/a', 'n/a')]), min_entries=10)
"""