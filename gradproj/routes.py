from flask import render_template, url_for, flash, redirect, request
from gradproj import app, db, bcrypt
from gradproj.forms import (RegistrationForm, LoginForm,
                            RequestResetFrom, ResetPasswordForm)
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')


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
    user = User.verify_reset_tokent(token)
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