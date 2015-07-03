# -*- coding: utf-8 -*-
from flask import render_template, flash,redirect,request, url_for,g
from . import auth
from flask.ext.login import logout_user,login_user, login_required,current_user
from .forms import LoginForm
from app.models import User, Ucitel_predmetu, Predmet, Povinny_predmet
from .. import db
from random import randint 


#flash hlasky
logged_in_msg=u"Úspešné prihlásenie."
# bad_teacher_passwd=u'Zadane heslo ucitela nie je spravne.'
# bad_passwd=u'Zadane heslo nie je spravne.'
cant_access_ldap_msg=u"Nedá sa pripojiť k LDAP serveru pre autentifikovanie ucitela."
# user_not_found_msg=u"Užívatel neexistuje."
bad_login_msg=u"Neúspešné prihlásenie. Skontrolujte prosím login a heslo."
logout_msg=u"Odhlásenie prebehlo úspešne."
title_msg=u'Prihlásenie'
ldap_server_down=-2
ldap_user_not_found=-1
ldap_wrong_passwd=0
ldap_auth_success=1
ucitelovo_priezvisko=""
ucitelovo_meno=""


@auth.route('/logout')
# @login_required
def logout():
	logout_user()
	flash(logout_msg,category='success')
	return redirect(url_for('auth.login'))

@auth.before_request
def before_request():
    g.user = current_user

def ldap_prihlasenie(form):
	import ldap
	result=None
	con=None

	try: 
		LDAP_BASE='ou=People,dc=fri,dc=uniza,dc=sk'
		scope=ldap.SCOPE_SUBTREE
		con = ldap.initialize('ldaps://pegasus.fri.uniza.sk')
		con.simple_bind_s("st_ucty","q2wa1s")
		result=con.search_s(LDAP_BASE, scope, "uid=%s" %form.login.data)
	except ldap.SERVER_DOWN,e:
		return ldap_server_down
	
	if not result:
		con.unbind()
		return ldap_user_not_found 
	
	# podla tohto sa zisti ci je to ucitel ci student
	gidNumber=result[0][1]['gidNumber'][0] 
	gid_student='14005'
	gid_ucitel='14004'

	# podla gidnumber zistim ci login patri ucitelovi, pretoze len ucitelov cez LDAP autentifikujem
	if gidNumber != gid_ucitel:
		con.unbind()
		return ldap_user_not_found

	name=result[0][1]['name'][0];
	cn=result[0][1]['cn'][0];
	
	ucitelovo_meno, ucitelovo_priezvisko =  name.split(" ")

	try:
		dn=result[0][0]
		con.simple_bind_s(dn,form.password.data)
		resauth=ldap_auth_success
	except ldap.INVALID_CREDENTIALS:
		resauth=ldap_wrong_passwd
	con.unbind()
	return resauth


def vytvor_uzivatela(login): 
	user=User(login=login,
			meno = ucitelovo_meno,
			priezvisko = ucitelovo_priezvisko)
	db.session.add(user)
	db.session.commit()
	return user

def prirad_ucitelovi_predmety(new_ucitel):
	#priradim ucitelovi nahodne predmety
	predmety_count = Predmet.query.count()
	for i in range(1,25):
		p = Predmet.query.offset(randint(0, predmety_count - 1)).first()

		#priradim mu predmety letnych semestrov
		success=False
		if Povinny_predmet.query.filter_by(predmet_id = p.id, semester=6).first():
			success=True
		elif Povinny_predmet.query.filter_by(predmet_id = p.id, semester=4).first():
			success=True
		elif Povinny_predmet.query.filter_by(predmet_id = p.id, semester=2).first():
			success=True

		if success:
			if Ucitel_predmetu.query.filter_by(predmet=p,user=new_ucitel).first() is None: 
			# ak neni este ucitelom toho predmetu tak ho nim spravim
				up = Ucitel_predmetu()
				up.predmet=p
				up.user=new_ucitel
				db.session.add(up)
				db.session.commit()


def prihlas_ucitela(login):
	user = User.query.filter_by(login = login).first() 
	if user is  None: 
		user= vytvor_uzivatela(login)
		prirad_ucitelovi_predmety(user)
	login_user(user)
	flash(logged_in_msg,category='success')

@auth.route('/login', methods = ['GET', 'POST'])
def login():
	# ak uz je prihlaseny tak ho presmerujem na index
	if current_user is not None and current_user.is_authenticated():
		if Ucitel_predmetu.query.filter_by(user_id = current_user.id).first() is None:
			return redirect(request.args.get('next') or url_for('student.index'))
		return redirect(request.args.get('next') or url_for('ucitel.index'))
		
	form = LoginForm()

	if form.validate_on_submit():

		#najprv skusam  zadany userlogin  autentifikovat cez LDAP

		"""
		workaround pre testovanie ucitelskeho uctu, pretoze nemam ziaden LDAP realny ucitelsky login+heslo
		takze moj falosny ucitel bude hocikdo, kdo ma v logine substring 'ucitel'
		"""
		if 'ucitel' in form.login.data:
			prihlas_ucitela(form.login.data)
			return redirect(request.args.get('next') or url_for('ucitel.zabezpecovane_predmety'))

		#skusim autentifikaciu ucitela cez LDAP
		resauth=ldap_user_not_found
		resauth=ldap_prihlasenie(form)

		if resauth==ldap_server_down:
			# neda sa pripojit k LDAP
			flash(cant_access_ldap_msg,category='danger')

		# if resauth==ldap_user_not_found:
		# 	# uzivatel neexistuje
		# 	flash(bad_login_msg,category='danger')

		if resauth==ldap_auth_success:
			#ucitel je autentifikovany upesne 
			#existuje uz v mojej DB tento ucitel?
			prihlas_ucitela(form.login.data)
			return redirect(request.args.get('next') or url_for('ucitel.zabezpecovane_predmety'))
		
		if resauth==ldap_wrong_passwd:
			# je ucitel,ale zadal zle heslo
			flash(bad_login_msg,category='danger')
			return render_template('auth/login.html', 
		    	title = title_msg,
		   		form = form)

		#ak som sa dostal az tu tak login nepatri ucitelovi, a skusim ho prihlasit ako studenta
		user = User.query.filter_by(login = form.login.data).first() 
		if user is not None:
			if Ucitel_predmetu.query.filter_by(user=user).first() is None:
				if user.verify_password(form.password.data):
					login_user(user)
					flash(logged_in_msg,category='success')
					return redirect(request.args.get('next') or url_for('main.index'))
		flash(bad_login_msg,category='danger')
	return render_template('auth/login.html', 
	    title = title_msg,
	    form = form)
