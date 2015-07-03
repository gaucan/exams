
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	WTF_CSRF_ENABLED = False
	SECRET_KEY = 'you-will-never-guess'
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True

class TestingConfig(Config):
	TESTING = True

class ProductionConfig(Config):
	PRODUCTION= True

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}
