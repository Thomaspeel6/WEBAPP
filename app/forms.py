from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import Destination



#singup forms and logina nd create trip forms

class LoginForm(FlaskForm):
    email_or_username = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=25, message='Username must be between 4 and 25 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Please enter a valid email address')
    ])
    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

class CreateTripForm(FlaskForm):
    name = StringField(
        'Trip Name',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={"placeholder": "Enter a name for your trip"}
    )
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    destinations = SelectMultipleField('Destinations', coerce=int)   
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Trip')

    