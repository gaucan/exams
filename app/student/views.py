# -*- coding: utf-8 -*-


from flask import render_template, flash,redirect,request, url_for,g,abort
from . import student # student blueprint
from app.models import Student_termin, Predmet, Termin, Student, Student_predmet
from flask.ext.login import logout_user,login_user, login_required,current_user

@student.before_request
@login_required
def before_request():
	g.user = current_user
	s=Student.query.filter_by(user_id=current_user.id).first()
	if  s is None:
		abort(403)
	g.student=current_user.students[0] #prvy student kt je priradeny k userovi

@student.route('/')
@student.route('/index')
def index():	
	return render_template('student/index.html')

#zobrazi vsetky  zapisane predmety
@student.route('/zap_predmety')
def zap_predmety():
	zap_predmety=[]
	for predmet in  g.student.predmety:
		zap_predmety.append(predmet.predmet)

	return render_template('student/zap_predmety.html',
							zap_predmety=zap_predmety)


#zobrazi vypisane terminy z daneho predmetua taktiez ci je 
# prave logged_in user( alebo user_id) na ne prihlaseny a ak hej tak sa tlacitko zmeni na 'odhlasit'
@student.route('/ukaz_terminy/<int:predmet_id>')
def ukaz_terminy(predmet_id):
	p = Predmet.query.filter_by(id=predmet_id).first()
	if p is None:
		abort(404)

	#exams= s.exams
	terminy= Termin.query.filter_by(predmet_id=p.id).order_by('zaciatok_skusky')

	tpl={}
	cnt={}
	for termin in terminy:
		je_prihlaseny = Student_termin.query.filter_by(student_id=g.student.os_cislo,termin_id=termin.id).first()
		if je_prihlaseny is None:
			tpl[termin]=False 
		else:
			tpl[termin]=True
		cnt[termin] = len(termin.prihlaseni_studenti)

	student_predmetu = Student_predmet.query.filter_by(predmet=p,student_id=g.student.os_cislo).first()

	return render_template('student/ukaz_terminy.html',
					terminy=terminy, 
					tpl=tpl,
					cnt=cnt,
					student_predmetu=student_predmetu,
					predmet=p)

# @student.route('/moje_terminy')
# @student_required
# def moje_terminy
# 	terminy=[]
# 	for i in  g.student.st:
# 		terminy.append(i.termin)
# 	return 