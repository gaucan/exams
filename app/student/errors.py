from flask import render_template
from . import student
from app import db

@student.errorhandler(404)
def page_not_found(error):
	return render_template('student/404.html'), 404


@student.errorhandler(403) 
def forbidden(error):
	db.session.rollback()
	return render_template('student/403.html'), 403
