# -*- coding: utf-8 -*-

from flask import render_template, flash,redirect,request, url_for,g,abort,jsonify
from . import ucitel # ucitel blueprint
from forms import TerminForm
from app import db
from app.models import Student_termin, Predmet, Termin,Ucitel_predmetu,Student_predmet, Miestnost
from flask.ext.login import logout_user,login_user, login_required,current_user
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,SelectField,validators,FieldList
from flask_weasyprint  import HTML, render_pdf

# @ucitel.route('/hello')
# def hello_html():
#     return render_template('ucitel/index.html')

# @ucitel.route('/hello.pdf')
# def hello_pdf():
#     # Make a PDF from another view
#     return render_pdf(url_for('ucitel.hello_html',follow_redirects=True))

# Alternatively, if the PDF does not have a matching HTML page:
@ucitel.route('/termin<int:termin_id>.pdf')
def termin_pdf(termin_id):

	termin = Termin.query.get(termin_id)
	abort(404) if termin is None else False
	

	zoznam=[]
	for student_terminu in termin.prihlaseni_studenti:
	 	sp = Student_predmet.query.filter_by(student=student_terminu.student,predmet=termin.predmet).first()
	 	zoznam.append(sp)

	# Make a PDF straight from HTML in a string.
	html = render_template('ucitel/template_pre_pdf.html',
		prihlaseni_studenti=zoznam)
	return render_pdf(HTML(string=html))

@ucitel.before_request
@login_required
def before_request():
	g.user = current_user

	if Ucitel_predmetu.query.filter_by(user_id=g.user.id).first() is None:
		abort(404)
    # print g.user.up
    # g.ucitel=g.user.up[0] #prvy student kt je priradeny k userovi

@ucitel.route('/')
@ucitel.route('/index')
def index():	
	return render_template('ucitel/index.html')

# @je_ucitel_predmetu(predmet_id)
@ucitel.route('/zabezpecovane_predmety')
def zabezpecovane_predmety():	
	zabezpecovane_predmety=[]
	for predmet in g.user.vyucovane_predmety:
		zabezpecovane_predmety.append(predmet.predmet)
	return render_template('ucitel/zabezpecovane_predmety.html',
		zabezpecovane_predmety=zabezpecovane_predmety)



#zobrazi vypisane terminy z daneho predmetua taktiez ci je 
@ucitel.route('/ukaz_terminy/<int:predmet_id>')
def ukaz_terminy(predmet_id):
	predmet = Predmet.query.filter_by(id=predmet_id).first()
	if predmet is None:
		abort(404)

	terminy= Termin.query.filter_by(predmet_id=predmet.id).order_by('zaciatok_skusky')

	cnt={}
	for termin in terminy:
		cnt[termin] = len(termin.prihlaseni_studenti)


	return render_template('ucitel/ukaz_terminy.html',
					terminy=terminy, 
					cnt=cnt,
					predmet=predmet)

#editovanie terminu
@ucitel.route('/edituj_termin/<int:termin_id>',methods = ['GET', 'POST'])
def edituj_termin(termin_id):
	termin = Termin.query.filter_by(id=termin_id).first()
	if termin is None:
		abort(404)

	form = TerminForm()
	# text pre labely zobrazujuce sa nad inputfieldom
	form.zaciatok_skusky_datum.label.text=u'Začiatok skúšky: dátum'
	form.zaciatok_skusky_datum.data=termin.zaciatok_skusky.strftime("%d/%m/%Y")
	form.zaciatok_skusky_cas.label.text=u'Začiatok skúšky: čas'
	form.zaciatok_skusky_cas.data=termin.zaciatok_skusky.strftime("%I:%M %p")
	form.uzavierka_prihlasovania_datum.label.text=u'Uzávierka prihlasovania: dátum'
	form.uzavierka_prihlasovania_datum.data=termin.uzavierka_prihlasovania.strftime("%d/%m/%Y")
	form.uzavierka_prihlasovania_cas.label.text=u'Uzávierka prihlasovania: čas'
	form.uzavierka_prihlasovania_cas.data=termin.uzavierka_prihlasovania.strftime("%I:%M %p")
	form.miestnost.label.text=u'Miestnosť'
	form.kapacita.label.text=u'Kapacita'
	form.kapacita.data=termin.kapacita
	form.poznamka.label.text=u'Poznámka'
	form.poznamka.data=termin.poznamka

	#pripravene miestnosti pre selectfields
	miestnosti=[]
	for m in Miestnost.query.all():
		miestnosti.append((m.meno,m.meno+", kapacita:"+str(m.kapacita)))
	form.miestnost.choices=miestnosti

	if form.validate_on_submit():
		zaciatok_skusky = form.zaciatok_skusky_datum.data +" "+form.zaciatok_skusky_cas.data
		zaciatok_skusky = datetime.strptime(zaciatok_skusky, '%d/%m/%Y %I:%M %p')
		# print zaciatok_skusky
		uzavierka_prihlasovania = form.uzavierka_prihlasovania_datum.data +" "+form.uzavierka_prihlasovania_cas.data
		uzavierka_prihlasovania = datetime.strptime(uzavierka_prihlasovania, '%d/%m/%Y %I:%M %p')

		if uzavierka_prihlasovania > zaciatok_skusky:
			flash(u'Uzávierka prihlasovania musí byť skôr než začiatok skúšky',category='danger')
			return render_template('ucitel/edituj_termin.html',termin=termin,form=form)
		vybrana_miestnost=Miestnost.query.filter_by(meno=form.miestnost.data).first()
		if int(form.kapacita.data) > vybrana_miestnost.kapacita:
			flash(u'Prekročil si kapacitu danej miestnosti',category='danger')
			return render_template('ucitel/edituj_termin.html',termin=termin,form=form)

		# toto je to iste ako update nizsie
		# termin.miestnost=vybrana_miestnost
		# termin.zaciatok_skusky= zaciatok_skusky
		# termin.uzavierka_prihlasovania=uzavierka_prihlasovania
		# termin.kapacita=int(form.kapacita.data)
		# termin.poznamka=form.poznamka.data

		rows_changed = Termin.query.filter_by(id=termin_id).update(dict(
			miestnost_id=vybrana_miestnost.id,
		zaciatok_skusky= zaciatok_skusky,
		uzavierka_prihlasovania=uzavierka_prihlasovania,
		kapacita=int(form.kapacita.data),
		poznamka=form.poznamka.data
			))
		db.session.commit()
		flash('Úspešne upravená skúška',category='success')
		return redirect(url_for('ucitel.ukaz_terminy',
						predmet_id=termin.predmet.id))

	return render_template('ucitel/edituj_termin.html',
					termin=termin,
					form=form)


@ucitel.route('/vytvor_skusku/<int:predmet_id>', methods = ['GET', 'POST'])
def vytvor_skusku(predmet_id):

	if Ucitel_predmetu.query.filter_by(predmet_id=predmet_id,user=g.user).first() is None:
		flash('Nezabezpecujes tento predmet',category='danger')
		abort(404)

	predmet = Predmet.query.filter_by(id=predmet_id).first()
	if predmet is None:
		abort(404)

	form = TerminForm()
	# text pre labely zobrazujuce sa nad inputfieldom
	form.zaciatok_skusky_datum.label.text='Zaciatok skusky: datum'
	form.zaciatok_skusky_cas.label.text='Zaciatok skusky: cas'
	form.uzavierka_prihlasovania_datum.label.text='Uzavierka prihlasovania: datum'
	form.uzavierka_prihlasovania_cas.label.text='Uzavierka prihlasovania: cas'
	form.kapacita.label.text='Kapacita'
	form.poznamka.label.text='Poznamka'
	form.miestnost.label.text='Miestnost'

	#pripravene miestnosti pre selectfields
	miestnosti=[]
	for m in Miestnost.query.all():
		miestnosti.append((m.meno,m.meno+", kapacita:"+str(m.kapacita)))
	form.miestnost.choices=miestnosti

	if form.validate_on_submit():
		zaciatok_skusky = form.zaciatok_skusky_datum.data +" "+form.zaciatok_skusky_cas.data
		zaciatok_skusky = datetime.strptime(zaciatok_skusky, '%d/%m/%Y %I:%M %p')
		# print  zaciatok_skusky.strftime('%d/%m/%Y %H:%M')
		uzavierka_prihlasovania = form.uzavierka_prihlasovania_datum.data +" "+form.uzavierka_prihlasovania_cas.data
		uzavierka_prihlasovania = datetime.strptime(uzavierka_prihlasovania, '%d/%m/%Y %I:%M %p')

		if uzavierka_prihlasovania > zaciatok_skusky:
			flash('Uzavierka prihlasovania musi byt skor nez zaciatok skusky',category='danger')
			# return redirect(url_for('ucitel.vytvor_skusku',
						# predmet_id=predmet_id))
			return render_template('ucitel/vytvor_skusku.html',form=form)

		vybrana_miestnost=Miestnost.query.filter_by(meno=form.miestnost.data).first()
		if int(form.kapacita.data) > vybrana_miestnost.kapacita:
			flash('Prekrocil si kapacitu danej miestnosti',category='danger')
			# return redirect(url_for('ucitel.vytvor_skusku',
						# predmet_id=predmet_id))
			return render_template('ucitel/vytvor_skusku.html',form=form)


		novy_termin = Termin(
			predmet=predmet,
			zaciatok_skusky= zaciatok_skusky,
			uzavierka_prihlasovania=uzavierka_prihlasovania,
			kapacita=form.kapacita.data,
			poznamka=form.poznamka.data,
			miestnost=vybrana_miestnost
			)

		db.session.add(novy_termin)
		db.session.commit()
		flash('Uspesne vytvorena skuska',category='success')
		return redirect(url_for('ucitel.ukaz_terminy',
						predmet_id=predmet_id))
	return render_template('ucitel/vytvor_skusku.html',form=form)

def ucitel_OK(predmet_id):
	
	#vyucuje prihlaseny ucitel tento predmet?
	up =Ucitel_predmetu.query.filter_by(user_id=g.user.id,predmet_id=predmet_id).first()
	if up is None:
		abort(403)


# @ucitel.route('/_manazuj_predmet_json/<int:predmet_id>', defaults={'zapocet': 'no','termin_id':0}, methods = ['GET', 'POST']) 
@ucitel.route('/_manazuj_predmet_json/<int:predmet_id>/<int:termin_id>/<zapocet>', methods = ['GET', 'POST'])
def _manazuj_predmet_json(predmet_id,termin_id,zapocet):

	predmet = Predmet.query.filter_by(id=predmet_id).first()
	if predmet is None:
		abort(404)

	ucitel_OK(predmet_id)

	studenti_predmetu=predmet.studenti_predmetu
	# print len(studenti_predmetu)

	if zapocet == 'yes':
		studenti_predmetu_so_zapoctom=[]
		for student_predmetu in studenti_predmetu:
			if student_predmetu.body_za_semester >= predmet.zapocet: # ma dost bodov?
				studenti_predmetu_so_zapoctom.append(student_predmetu)
		studenti_predmetu=studenti_predmetu_so_zapoctom

	is_filtered_by_termin=False
	if termin_id != 0:
		studenti_tohto_terminu=[]
		najdeny_termin=None
		for termin in predmet.terminy:
			if termin.id==termin_id:
				najdeny_termin=termin
		abort(404) if najdeny_termin is None else False
			
			# flash('spatna id terminu',category='danger')
			# return render_template('ucitel/manazuj_predmet',
			# 			predmet_id=predmet_id))
		for studentov_termin in najdeny_termin.prihlaseni_studenti:
			studentov_termin.student #ziskam studenta
			sp = Student_predmet.query.filter_by(student=studentov_termin.student, predmet_id=predmet_id).first()
			abort(404) if sp is None else False
			studenti_tohto_terminu.append(sp) 
		studenti_predmetu=studenti_tohto_terminu
		is_filtered_by_termin=True

	
	form =  vytvor_formular_pre_manazovanie_studentov(studenti_predmetu)
	
	nake_html =  render_template('ucitel/manazuj_predmet_json.html',
			form=form,
			predmet = predmet,
			studenti_predmetu=studenti_predmetu,
			)

	return jsonify(html=nake_html)


@ucitel.route('/manazuj_predmet/<int:predmet_id>', defaults={'zapocet': 'no','termin_id':0}, methods = ['GET', 'POST']) 
@ucitel.route('/manazuj_predmet/<int:predmet_id>/<int:termin_id>/<zapocet>', methods = ['GET', 'POST'])
# @ucitel.route('/manazuj_predmet/<int:predmet_id>/<int:termin_id>/', defaults={'zapocet': 'no'}, methods = ['GET', 'POST']) 
#ak nie je zadany parameter pre zapocet v URL tak default je "no" a teda zobraz aj studentov bez zapoctu
def manazuj_predmet(predmet_id,termin_id,zapocet):
	#predmet neexistuje
	predmet = Predmet.query.filter_by(id=predmet_id).first()
	if predmet is None:
		abort(404)

	ucitel_OK(predmet_id)

	studenti_predmetu=predmet.studenti_predmetu
	# print len(studenti_predmetu)

	if zapocet == 'yes':
		studenti_predmetu_so_zapoctom=[]
		for student_predmetu in studenti_predmetu:
			if student_predmetu.body_za_semester >= predmet.zapocet: # ma dost bodov?
				studenti_predmetu_so_zapoctom.append(student_predmetu)
		studenti_predmetu=studenti_predmetu_so_zapoctom

	is_filtered_by_termin=False
	if termin_id != 0:
		studenti_tohto_terminu=[]
		najdeny_termin=None
		for termin in predmet.terminy:
			if termin.id==termin_id:
				najdeny_termin=termin
		abort(404) if najdeny_termin is None else False
			
			# flash('spatna id terminu',category='danger')
			# return render_template('ucitel/manazuj_predmet',
			# 			predmet_id=predmet_id))
		for studentov_termin in najdeny_termin.prihlaseni_studenti:
			studentov_termin.student #ziskam studenta
			sp = Student_predmet.query.filter_by(student=studentov_termin.student, predmet_id=predmet_id).first()
			abort(404) if sp is None else False
			studenti_tohto_terminu.append(sp) 
		studenti_predmetu=studenti_tohto_terminu
		is_filtered_by_termin=True

	
	form =  vytvor_formular_pre_manazovanie_studentov(studenti_predmetu)
	
	if form.validate_on_submit():
		commitni_udaje_z_formulara(form,studenti_predmetu)

		return redirect(url_for('ucitel.manazuj_predmet',predmet_id=predmet_id))
	else:
		return render_template('ucitel/manazuj_predmet.html',
			form=form,
			predmet = predmet,
			studenti_predmetu=studenti_predmetu,
			terminy=predmet.terminy,
			tento_termin=Termin.query.get(termin_id),
			is_filtered_by_termin=is_filtered_by_termin,
			termin_id=termin_id
			)

def commitni_udaje_z_formulara(form,studenti_predmetu):
	i =0
	for i, student_predmetu in enumerate(studenti_predmetu):
		student_predmetu.konecna_znamka = form.data['select0_%d' % i] #kkonecna znamka
		student_predmetu.body_za_semester = form.data['body_za_semester_%d' % i]

		student_predmetu.znamka1 = form.data['select1_%d' % i]
		student_predmetu.znamka2 = form.data['select2_%d' % i]
		student_predmetu.znamka3 = form.data['select3_%d' % i]

		student_predmetu.poznamka1 = form.data['poznamka1_%d' % i]
		student_predmetu.poznamka2 = form.data['poznamka2_%d' % i]
		student_predmetu.poznamka3 = form.data['poznamka3_%d' % i]

		student_predmetu.datum1 = datetime.strptime(form.data['datum1_%d' % i], "%m/%d/%y") if form.data['datum1_%d' % i] else  student_predmetu.datum1
		student_predmetu.datum2 = datetime.strptime(form.data['datum2_%d' % i], "%m/%d/%y") if form.data['datum2_%d' % i] else  student_predmetu.datum2
		student_predmetu.datum3 = datetime.strptime(form.data['datum3_%d' % i], "%m/%d/%y") if form.data['datum3_%d' % i] else  student_predmetu.datum3
	db.session.commit()

def vytvor_formular_pre_manazovanie_studentov(studenti_predmetu):
	class F(Form):
		pass

	count=0
	
	for student_predmetu in studenti_predmetu:

		#konecna znamka
		setattr(F, 'select0_%d'%count, SelectField(student_predmetu.student.user.priezvisko,
	                                    validators=[validators.optional()],
	                                    choices=[('A', 'A'), ('B', 'B'), ('C', 'C'),
	                                     ('D', 'D'), ('E', 'E'), ('FX', 'FX'),
	                                     ('n/a', 'n/a')],
	                                     default=student_predmetu.konecna_znamka if student_predmetu.konecna_znamka is not None else 'FX'))
		setattr(F, 'body_za_semester_%d'%count, TextField("", validators=[validators.optional()], 
								default=student_predmetu.body_za_semester if student_predmetu.body_za_semester is not None else 0))

		setattr(F, 'select1_%d'%count, SelectField(student_predmetu.student.user.priezvisko,
	                                    validators=[validators.optional()],
	                                    choices=[('A', 'A'), ('B', 'B'), ('C', 'C'),
	                                     ('D', 'D'), ('E', 'E'), ('FX', 'FX'),
	                                     ('n/a', 'n/a')],
	                                     default=student_predmetu.znamka1 if student_predmetu.znamka1 is not None else 'FX'))
		setattr(F, 'poznamka1_%d'%count, TextField("", validators=[validators.optional()],default=student_predmetu.poznamka1))
		setattr(F, 'datum1_%d'%count, TextField("", validators=[validators.optional()],
			default=student_predmetu.datum1.strftime("%x") if student_predmetu.datum1 else ""))


		setattr(F, 'select2_%d'%count, SelectField(student_predmetu.student.user.priezvisko,
	                                    validators=[validators.optional()],
	                                    choices=[('A', 'A'), ('B', 'B'), ('C', 'C'),
	                                     ('D', 'D'), ('E', 'E'), ('FX', 'FX'),
	                                     ('n/a', 'n/a')],
	                                     default=student_predmetu.znamka2 if student_predmetu.znamka2 is not None else 'FX'))
		setattr(F, 'poznamka2_%d'%count, TextField("", validators=[validators.optional()],default=student_predmetu.poznamka2))
		setattr(F, 'datum2_%d'%count, TextField("", validators=[validators.optional()],
			default=student_predmetu.datum2.strftime("%x") if student_predmetu.datum2 else ""))


		setattr(F, 'select3_%d'%count, SelectField(student_predmetu.student.user.priezvisko,
	                                    validators=[validators.optional()],
	                                    choices=[('A', 'A'), ('B', 'B'), ('C', 'C'),
	                                     ('D', 'D'), ('E', 'E'), ('FX', 'FX'),
	                                     ('n/a', 'n/a')],
	                                     default=student_predmetu.znamka3 if student_predmetu.znamka3 is not None else 'FX'))
		setattr(F, 'poznamka3_%d'%count, TextField("", validators=[validators.optional()],default=student_predmetu.poznamka3))
		setattr(F, 'datum3_%d'%count, TextField("", validators=[validators.optional()],
			default=student_predmetu.datum3.strftime("%x") if student_predmetu.datum3 else ""))

		count +=1
	return F()

	
