# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from .. import  db, lm
from .forms import FeedbackForm
# from ..models import User,Exam,Attempt,Subject
from ..models import User, Student

#-------- form shit
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,SelectField,validators,FieldList
from wtforms.validators import Required
#---------
from . import main # import main blueprint

"""
presmerujem na index podla toho ci je prihlaseny user student ci ucitel
"""
@main.route('/')
@main.route('/index')
@login_required
def index():	
	if Student.query.filter_by(user_id= current_user.id).first() is None:
		return redirect(url_for('ucitel.index'))
	return redirect(url_for('student.index'))


@main.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():	

	form = FeedbackForm()

	is_ucitel=False
	if Student.query.filter_by(user_id= current_user.id).first() is None:
		is_ucitel=True

	if form.validate_on_submit():
	    flash(u'Vaše pripomienky boli úspešne odoslané vývojárom.','success')
	    return redirect(url_for('main.index'))

	return render_template('main/feedback.html', 
		form=form,
		is_ucitel=is_ucitel,)


@main.route('/json_index')
def json_index():
	return render_template('json_index.html')


@main.route('/_add_numbers')
def add_numbers():
	a = request.args.get('a', 0, type=int)
	b = request.args.get('b', 0, type=int)
	c = request.args.get('random_word')
	return jsonify(result=a + b, c=c)

