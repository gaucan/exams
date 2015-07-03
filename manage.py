#!/usr/bin/env python
import os
from app import create_app, db
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
	from app.models import Termin, Miestnost, Predmet,Student_termin, Student, Odbor,User,Povinny_predmet,Ucitel_predmetu,Student_predmet
	return dict(app=app,
	 db=db,
	  User=User,
	  Termin=Termin, 
	  Miestnost=Miestnost,
	   Predmet=Predmet,
	   Student_termin=Student_termin, 
	   Student=Student, 
	   Odbor=Odbor,
	   Povinny_predmet=Povinny_predmet,
	   Ucitel_predmetu=Ucitel_predmetu,
	   Student_predmet=Student_predmet
	  )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host="0.0.0.0", port=6969, threaded=True))

@manager.command
def test():
	"""Run the unit tests."""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def profile(length=10, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
	profile_dir=profile_dir)
	app.run(host="0.0.0.0", port=6969, threaded=True)

if __name__ == '__main__':
	manager.run()
