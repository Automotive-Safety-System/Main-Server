from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from gradproj.models import User, Vehicle

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

# username validation function 
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. please choose another one!')

# Email validation function 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. please choose another one!')

# Phone number validation function 
    def validate_phone(self, phone):
        user = User.query.filter_by(phone_number=phone.data).first()
        if user:
            raise ValidationError('That phone is taken. please choose another one!')


# Login form 
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Reset email and password form
class RequestResetFrom(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. you must register first.')


# Make a new password
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# UpdateAccount Form 
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min= 2, max= 20)])
    first_name = StringField('First Name', validators=[ DataRequired()])
    last_name = StringField('Last Name ', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=11, max=12)])
    country = StringField('Country', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = StringField('ZIP')
    street = StringField('Street', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

# username validation function 
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. please choose another one!')

# Email validation function 
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. please choose another one!')

# Phone number validation function 
    def validate_phone(self, phone):
        if phone.data != current_user.phone_number:
            user = User.query.filter_by(phone_number=phone.data).first()
            if user:
                raise ValidationError('That phone is taken. please choose another one!')

# Oberserver form
class ObserverForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min= 2, max= 20)])
    submit = SubmitField('Add')

# username validation function
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
           raise ValidationError('Username doesn\'t exist.')
        if username.data == current_user.username:
            raise ValidationError('You can\'t add yourself as an observer!')

# Vehicle form
class VehicleForm(FlaskForm):
    vehicle_model = StringField('Vehicle Model', validators=[DataRequired(), Length(min= 2, max= 20)])
    plate_number = StringField('Plate Number', validators=[DataRequired(), Length(min= 2, max= 8)])
    submit = SubmitField('Add')

    def validate_plate_number(self, plate_number):
        vehicle = Vehicle.query.filter_by(plate_number=plate_number.data).first()
        if vehicle:
            raise ValidationError('That plate number exists.')

# Emergency form
class EmergencyForm(FlaskForm):
    cellphone = StringField('Cell Phone', validators=[DataRequired(), Length(min=11, max=12)])
    submit = SubmitField('Add')
