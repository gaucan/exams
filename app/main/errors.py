from flask import render_template
from . import main
from app import db


"""
.app_errorhandler - globalne
.errorhandler - len errory z daneho blueprint
"""
@main.app_errorhandler(404)
def page_not_found(error):
	return render_template('main/404.html'), 404


@main.app_errorhandler(403) 
def forbidden(error):
	return render_template('main/403.html'), 403

'''
If the exception was triggered by a database error then 
the database session is going to arrive in an invalid state, 
so we have to roll it back in case a working session is needed 
for the rendering of the template for the 500 error.
'''
@main.app_errorhandler(500) 
def internal_server_error(error):
	db.session.rollback()
	return render_template('main/500.html'), 500

