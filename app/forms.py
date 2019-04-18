from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddActivityForm(FlaskForm):
    activitytype = SelectField('Activity:', validators=[DataRequired()], coerce=int)
    date = DateField(label='Date:')
    submit = SubmitField('Add')

class EditActivityForm(FlaskForm):
    activitytype = SelectField('Activity:', validators=[DataRequired()], coerce=int)
    date = DateField(label='Date:')
    submit = SubmitField('Save')

class AddActivityTypeForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    nsfw = BooleanField('NSFW')
    submit = SubmitField('Add')

class ImportActivityForm(FlaskForm):
    file = FileField('', validators=[DataRequired()]) # TODO: Validate File
    submit = SubmitField('Import')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email address', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
