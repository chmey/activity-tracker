from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddActivityForm(FlaskForm):
    activitytype = SelectField('Activity:', validators=[DataRequired()], coerce=int)
    date = DateField(label='Date:')
    submit = SubmitField('Add')
