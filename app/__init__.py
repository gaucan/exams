from flask import Flask, redirect, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from pprint import pprint
from config import config

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'auth.login'
lm.login_message = u"Tato stranka vyzaduje prihlasenie."
lm.login_message_category = "danger"
lm.session_protection = 'strong'
@lm.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login',next=request.path))


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])

	from main import main as main_blueprint # reg main blue
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint # reg auth blue 
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from .student import student as student_blueprint # reg student blue 
	app.register_blueprint(student_blueprint, url_prefix='/student')

	from .ucitel import ucitel as ucitel_blueprint # reg student blue 
	app.register_blueprint(ucitel_blueprint, url_prefix='/ucitel')

	config[config_name].init_app(app)
	db.init_app(app)
	lm.init_app(app)
	
	# pprint(lm.__dict__)# pretty prints array 
	# for key,value in lm.__dict__.iteritems(): print key,value #pretty print easy spusobem
	return app




