from flask import render_template
from . import ucitel
from app import db

@ucitel.errorhandler(404)
def page_not_found(error):
	return render_template('ucitel/404.html'), 404


@ucitel.errorhandler(403) 
def forbidden(error):
	db.session.rollback()
	return render_template('ucitel/403.html'), 403
