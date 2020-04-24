import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from gradproj import app, db, bcrypt
from gradproj.forms import (RegistrationForm, LoginForm,
                            RequestResetFrom, ResetPasswordForm,
                            UpdateAccountForm)
from gradproj.models import * 
from flask_login import login_user, current_user, logout_user, login_required
from gradproj.helpers import send_reset_email

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, 
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=hashed_password,
                    phone_number=form.phone.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'warning')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('welcome', 'warning')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login is unsuccessful.', 'warning')
        return render_template('login.html', title='Login', form=form)
    except:
        return redirect(url_for('home'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/dashboard")
@login_required
def dashboard():
    data = {
            'username' : 'Khaled Hisham',
            'profile_picture' : '../static/img/logo.png',
            'accelerometer' : '50',
            'location' : 'NewYork',
            'observe_requests' : '5',
            'status' : 'Parked'
        }
    image_file =    url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('dashboard.html',  image_file = image_file ,title = 'HOME' ,data = data)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'warning')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form = form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That as an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('your password has been updated!', 'warning')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Make a new password', form = form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)  
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)

    output_size = (125,125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    
    return picture_filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.first_name.data
        current_user.email = form.email.data        
        current_user.phone_number = form.phone.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone_number
    image_file =    url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',  image_file = image_file ,title = 'HOME', form = form)
