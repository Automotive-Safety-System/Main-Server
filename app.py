import os
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html', title='Register', form= form)
    
@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title= 'Login', form= form)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')