from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, DeviceTypes

class LoginForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired()])
	password = StringField('Password',validators=[DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
	username = StringField('Username')
	email = StringField('Email')
	password = PasswordField('Password',validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	"""
		When you add any methods that match the pattern validate_<field_name>,
		WTForms takes those as custom validators and invokes them
		in addition to the stock validators.

	"""
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

class EditDeviceForm(FlaskForm):
	name = StringField('Name',validators=[DataRequired()])
	#dev_type = SelectField('Device Type', choices=[(d.type,d.type) for d in DeviceTypes.query.order_by('type')])
	#dev_user = SelectField('Device User', choices=[(u.username,u.username) for u in User.query.order_by('username')])
	submit = SubmitField('Update')

class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Request Password Reset')