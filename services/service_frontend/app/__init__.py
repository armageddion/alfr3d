from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
import sys

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)

	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	bootstrap.init_app(app)

	from app import routes, models, errors

	if not app.debug:
		if app.config['MAIL_SERVER']:
			auth = None
			if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
				auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
			secure = None
			if app.config['MAIL_USE_TLS']:
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
				fromaddr='no-reply@' + app.config['MAIL_SERVER'],
				toaddrs=app.config['ADMINS'], subject='Alfr3d Failure',
				credentials=auth, secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)

		# For container, log to stdout
		console_handler = logging.StreamHandler(sys.stdout)
		console_handler.setFormatter(logging.Formatter(
			'%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
		console_handler.setLevel(logging.INFO)
		app.logger.addHandler(console_handler)

		app.logger.setLevel(logging.INFO)
		app.logger.info('Cassiop3ia web startup')

	return app	