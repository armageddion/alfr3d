from datetime import datetime
from time import time
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(128), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(256))
	last_online = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	state = db.Column(db.Integer, db.ForeignKey('states.id'))
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))
	type = db.Column(db.Integer, db.ForeignKey('user_types.id'))

	# Note: relationship is referenced by the model class --> Post
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	devices = db.relationship('Device', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

class UserTypes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(64), index=True)
	users = db.relationship('User', backref='user_type', lazy='dynamic')

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	# Note: relationship is referenced by the table name --> user
	# which is automatically in lowercase (thanks SQLAlchemy)
	# mutli-word model names become snake_case
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Device(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True)
	IP = db.Column(db.String(15))
	MAC = db.Column(db.String(17), unique=True)
	state = db.Column(db.Integer, db.ForeignKey('states.id'))
	last_online = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	device_type = db.Column(db.Integer, db.ForeignKey('device_types.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

class DeviceTypes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(64), index=True, unique=True)
	devices = db.relationship('Device', backref='device_type_rel', lazy='dynamic')

class States(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.String(8), index=True, unique=True)
	devices = db.relationship('Device', backref='device_state', lazy='dynamic')
	users = db.relationship('User', backref='user_state', lazy='dynamic')

class Routines(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), index=True)
	time = db.Column(db.Time)
	enabled = db.Column(db.Boolean, default=False)
	triggered = db.Column(db.Boolean, default=False)

	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

class Environment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	latitude = db.Column(db.Integer)
	longitude = db.Column(db.Integer)
	city = db.Column(db.String(64))
	state = db.Column(db.String(64))
	country = db.Column(db.String(64))
	IP = db.Column(db.String(15))
	low = db.Column(db.Integer)
	high = db.Column(db.Integer)
	description = db.Column(db.String(64))
	sunrise = db.Column(db.DateTime)
	sunset = db.Column(db.DateTime)

	users = db.relationship('User', backref='environment', lazy='dynamic')
	devices = db.relationship('Device', backref='environment', lazy='dynamic')
	routines = db.relationship('Routines', backref='environment', lazy='dynamic')

class Config(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(45))
	value = db.Column(db.String(45))

class Quips(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(64))
	quips = db.Column(db.String(256))

@login.user_loader
def load_user(id):
	return User.query.get(int(id))
