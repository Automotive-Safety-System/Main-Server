import os
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, jsonify
from gradproj import app, db, bcrypt
from gradproj.forms import (RegistrationForm, LoginForm,
                            RequestResetFrom, ResetPasswordForm,
                            UpdateAccountForm, ObserverForm,
                            VehicleForm, EmergencyForm)
from gradproj.models import * 
from flask_login import login_user, current_user, logout_user, login_required
from gradproj.helpers import send_reset_email
import reverse_geocoder as rg
import ast



@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/register", methods=['POST', 'GET'])
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
        address = Address.query.filter_by(country = form.country.data,
                          state = form.state.data,
                          city = form.city.data,
                          street = form.street.data,
                          postal_code= form.zip_code.data).first()
        if address is None:
            address = Address(country = form.country.data,
                              state = form.state.data,
                              city = form.city.data,
                              street = form.street.data,
                              postal_code= form.zip_code.data)
        try:
            db.session.add(address)
            db.session.add(user)
            address.users.append(user)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
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


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    vehicles = []
    accidents = []
    pending_observer_requests = []
    observers = []
    for vehicle in current_user.user_vehicle:
        vehicles.append({
                'vehicle_model' : vehicle.vehicle_model,
                'accelerometer' : vehicle.accelerometer,
                'last_location' : vehicle.location,
                'status' : vehicle.status,
                'update_date' : vehicle.update_date.strftime('%Y/%m/%d')
        })
        for accident in vehicle.accidents:
            accidents.append({
                'vehicle_model' : vehicle.vehicle_model,
                'plate_number' : vehicle.plate_number,
                'location' : accident.location,
                'accelerometer' : accident.accelerometer,
                'date' : accident.time_date.strftime("%d/%m/%Y, %H:%M:%S")

            })
    for observed in current_user.observers:
        for observer in observed.observers:
            if current_user.equals(observer):
                observed_vehicles = []
                for vehicle in observed.user_vehicle:
                    observed_vehicles.append({
                            'vehicle_model' : vehicle.vehicle_model,
                            'accelerometer' : vehicle.accelerometer,
                            'plate_number' : vehicle.plate_number,
                            'last_location' : vehicle.location,
                            'status' : vehicle.status,
                    })
                observers.append({
                    'username' : observed.username,
                    'image_file' : url_for('static', filename='profile_pics/' + observed.image_file),
                    'vehicles' : observed_vehicles
                })

    users = User.query.all()
    for user in users:
        for observer in user.observers:
            if current_user.equals(observer) and observer.observers ==[]:
                pending_observer_requests.append({
                    'username' : user.username
                })
            else:
                for observed in observer.observers:
                    if not observed.equals(user):
                        pending_observer_requests.append({
                        'username' : user.username
                        })

    data = {
            'vehicles' : vehicles,
            'observers' : observers,
            'pending_observer_requests' : pending_observer_requests,
            'accidents' : accidents
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
        form.country.data = current_user.address.country
        form.state.data = current_user.address.state
        form.city.data = current_user.address.city
        form.street.data = current_user.address.street
        form.zip_code.data = current_user.address.postal_code
    image_file =    url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',  image_file = image_file ,title = 'PROFILE', form = form)


@app.route("/observer", methods=['GET', 'POST'])
@login_required
def observer():
    form = ObserverForm()
    if form.validate_on_submit():
        try:
            current_user.observers.append(User.query.filter_by(username=form.username.data).first())
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect(url_for('observer'))
    return render_template('observer.html' ,title = 'OBSERVER', form = form)

@app.route("/vehicle", methods=['GET', 'POST'])
@login_required
def vehicle():
    form = VehicleForm()
    vehicle = Vehicle.query.filter_by(plate_number= form.plate_number.data).first()
    if vehicle is None:
        vehicle = vehicle(cellphone=form.cellphone.data)
    if form.validate_on_submit():
        vehicle = Vehicle(vehicle_model=form.vehicle_model.data, plate_number=form.plate_number.data)
        try:
            db.session.add(vehicle)
            current_user.user_vehicle.append(vehicle)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('vehicle'))
    return render_template('vehicle.html' ,title = 'VEHICLE', form = form)

@app.route('/dashboard/observer/<observer_username>/delete', methods=['DELETE'])
@login_required
def delete_observers(observer_username):
    print(observer_username)
    error = False
    try:
        user_observers = current_user.observers
        for ob in user_observers:
            if ob.username == observer_username:
                observer = ob
        current_user.observers.remove(observer)
        for observed in observer.observers:
            if observed.equals(current_user):
                observer.observers.remove(observed)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

@app.route('/dashboard/observer/request/<request_username>/delete', methods=['DELETE'])
@login_required
def delete_observer_request(request_username):
    print(request_username)
    error = False
    try:
        user = User.query.filter_by(username=request_username).first()
        for ob in user.observers:
            if ob.equals(current_user):
                user.observers.remove(current_user)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/dashboard/observer/request/<request_username>/accept', methods=['POST'])
@login_required
def accept_observer_request(request_username):
    print(request_username)
    error = False
    try:
        user = User.query.filter_by(username=request_username).first()
        current_user.observers.append(user)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

@app.route("/emergency", methods=['GET', 'POST'])
@login_required
def emergency():
    form = EmergencyForm()
    if form.validate_on_submit():
        cellphone = Contact.query.filter_by(cellphone= form.cellphone.data).first()
        if cellphone is None:
            cellphone = Contact(cellphone=form.cellphone.data)
        try:
            db.session.add(cellphone)
            current_user.user_contact.append(cellphone)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect(url_for('emergency'))
    return render_template('emergency.html' ,title = 'EMERGENCY', form = form)

# API
@app.route('/api/receive', methods=['POST'])
def receive():
    print("shit")
    data = ast.literal_eval(request.get_json(force=True))
    # print(all_data + "\n")
    # data = ast.literal_eval(all_data['payload'])
    print(data)
    error = False
    try:
        user_vehicle = Vehicle.query.filter_by(vehicle_model=data['vehicle']).first()
        print(user_vehicle)
        if data['type'] == 'accelerometer':
            user_vehicle.accelerometer = data['accelerometer']
        elif data['type'] == 'location':
            coordinates = data['location']
            location = rg.search(coordinates)[0]['name'] + \
                       "," + " " + rg.search(coordinates)[0]['admin1']
            user_vehicle.location = location
        elif data['type'] == 'accident':
            time_date = datetime.now()
            coordinates = data['location']
            location = rg.search(coordinates)[0]['name'] + \
                       "," + " " + rg.search(coordinates)[0]['admin1']
            accelerometer = data['accelerometer']
            vehicle_id = user_vehicle.id
            accident = Accident(time_date=time_date,
                                location=location,
                                accelerometer=accelerometer,
                                vehicle_id=vehicle_id)
            db.session.add(accident)
            user_vehicle.accidents.append(accident)

        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})
