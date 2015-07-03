from . import db,lm
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin 
# UserMixin gives default implementation for is_authenticated is_active is_anonymous get_id

class User(UserMixin, db.Model):
    #__tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128)) # optional === nulable, default je True
    meno = db.Column(db.String(128))
    priezvisko = db.Column(db.String(128))
   
    students = db.relationship("Student", backref="user") 
    vyucovane_predmety = db.relationship("Ucitel_predmetu", backref="user") 

    @lm.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def validate_username(self, field):
        if User.query.filter_by(login=field.data).first():
            return false #uz existuje 
        return true
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User  %s , vola sa  %s %s>' % (self.login, self.meno,self.priezvisko)

class Predmet(db.Model):
    __tablename__ = 'predmet'
    id = db.Column(db.Integer, primary_key = True) 
    meno = db.Column(db.String(128), nullable=False, unique=True)
    zapocet = db.Column(db.Integer) # minimum bodov na ziskanie zapoctu
    povinne_predmety = db.relationship("Povinny_predmet", backref="predmet") 
    ucitelia_predmetu = db.relationship("Ucitel_predmetu", backref="predmet") 
    studenti_predmetu = db.relationship("Student_predmet", backref="predmet") 
    terminy = db.relationship("Termin", backref="predmet") 

    def __repr__(self):
        return '<predmet: %s>' % (self.meno)


class Odbor(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    meno = db.Column(db.String(128), nullable=False)
    studenti = db.relationship("Student", backref="odbor") 
    povinne_predmety = db.relationship("Povinny_predmet", backref="odbor") 

    def __repr__(self):
        return '<Odbor: %s>' % (self.meno)

class Student(db.Model):
    os_cislo = db.Column(db.Integer, primary_key = True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    odbor_id= db.Column(db.Integer,  db.ForeignKey('odbor.id'))
    rocnik= db.Column(db.Integer)
    skupina= db.Column(db.String(128))
    predmety = db.relationship("Student_predmet", backref="student")  
    terminy = db.relationship("Student_termin", backref="student") 

    # def __repr__(self):
    #     return '<Student: %s %s,oscislo %s,odbor %s, skupina:%s, rocnik:%s, zapis: %s>' % \
    #     (self.user.meno,  self.user.priezvisko,self.os_cislo,self.odbor.meno, self.skupina,  self.rocnik, self.datum_zapisu )

class Povinny_predmet(db.Model):
    predmet_id=db.Column(db.Integer, db.ForeignKey('predmet.id'),primary_key = True)
    odbor_id=db.Column(db.Integer, db.ForeignKey('odbor.id'),primary_key = True)
    semester=db.Column(db.Integer) # cislo semestra

    def __repr__(self):
        return '<Predmet %s je povinny pre odbor %s  v %s semestri >' % \
        (self.predmet.meno, self.odbor.meno, self.semester)

class Ucitel_predmetu(db.Model):
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True)
    predmet_id=db.Column(db.Integer, db.ForeignKey('predmet.id'),primary_key = True)

    def __repr__(self):
        return '<Ucitel %s %s, vyucuje predmet %s >' % \
        (self.user.meno, self.user.priezvisko, self.predmet.meno)

class Student_predmet(db.Model):
    __tablename__ = 'Student_predmet'
    student_id = db.Column(db.Integer, db.ForeignKey('student.os_cislo'),primary_key = True ) 
    predmet_id = db.Column(db.Integer, db.ForeignKey('predmet.id'),primary_key = True)
    body_za_semester =  db.Column(db.Integer)
    konecna_znamka =  db.Column(db.String(128))
    znamka1 = db.Column(db.String(128))   # znamka z studentovho prveho terminu
    poznamka1 = db.Column(db.String(8192)) # ucitelova poznamka k studentovmu prvemu terminu
    datum1 = db.Column(db.DateTime())   # datum skusky/vyhodnotenia studentovho prveho terminu
    
    znamka2 = db.Column(db.String(128))  # znamka z studentovho 2. terminu  , atd..
    poznamka2 = db.Column(db.String(8192)) 
    datum2 = db.Column(db.DateTime())
    
    znamka3 = db.Column(db.String(128))
    poznamka3 = db.Column(db.String(8192)) 
    datum3 = db.Column(db.DateTime()) 


    def __repr__(self):
        return '<Student %s %s navstevuje predmet %s,konecnaZnamka %s, bodyZaSemester %s>' % \
        (self.student.user.meno, self.student.user.priezvisko, self.predmet.meno,
         self.konecna_znamka, self.body_za_semester)

class Miestnost(db.Model):
    id =  db.Column(db.Integer,primary_key = True ) 
    meno = db.Column(db.String(128),  unique=True)
    kapacita = db.Column(db.Integer) 
    terminy = db.relationship("Termin", backref="miestnost") 


    def __repr__(self):
        return '<Miestnost %s s kapacitou %s >' % \
        (self.meno, self.kapacita)


class Termin(db.Model):
    id =  db.Column(db.Integer,primary_key = True ) 
    predmet_id = db.Column(db.Integer, db.ForeignKey('predmet.id'))
    miestnost_id = db.Column(db.Integer, db.ForeignKey('miestnost.id'))
    zaciatok_skusky = db.Column(db.DateTime())
    uzavierka_prihlasovania = db.Column(db.DateTime())
    kapacita = db.Column(db.Integer) 
    poznamka = db.Column(db.String(8192))
    prihlaseni_studenti = db.relationship("Student_termin", backref="termin") 

    def __repr__(self):
        return '<Termin z predmetu %s , v miestnosti %s, kapacita %s,   zacina %s  >' % \
        (self.predmet.meno, self.miestnost.meno, self.kapacita,  self.zaciatok_skusky)

class Student_termin(db.Model):
    termin_id = db.Column(db.Integer, db.ForeignKey('termin.id'),primary_key = True )
    student_id = db.Column(db.Integer, db.ForeignKey('student.os_cislo'),primary_key = True ) #oscislo studenta
   
    # def __repr__(self):
    #     return '<Student_termin %s %s %s %s %s   >' % \
    #     (self.termin , self.student, self.znamka, self.poznamka, self.datum_vyhodnotenia)



