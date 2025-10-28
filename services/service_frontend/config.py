import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	# Flask-WTF extension uses this to protect web forms against Cross-Site Request Forgery or CSRF
	SECRET_KEY = os.environ['SECRET_KEY']

	# Flask-SQLAlchemy uses this stuff
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

	SQLALCHEMY_TRACK_MODIFICATION = False

	# Mail stuff so that admin can get email reports
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['your-email@example.com']