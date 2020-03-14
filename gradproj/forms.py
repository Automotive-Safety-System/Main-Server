from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


# Registration Form 
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min= 2, max= 20)])
    first_name = StringField('First Name', validators=[ DataRequired()])
    last_name = StringField('Last Name ', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=11, max=12)])
    country = StringField('Country', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = StringField('ZIP')
    street = StringField('Street', validators=[DataRequired()])
    submit = SubmitField('Sign up')

# Login form 
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
