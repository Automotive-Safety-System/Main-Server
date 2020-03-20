from datetime import datetime
from gradproj import db, login_manager
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# get user by ID docerator 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


User_Address = db.Table('user_address',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('address_id', db.Integer, db.ForeignKey('address.id')),
    UniqueConstraint('user_id','address_id')
    )

User_Contact = db.Table('user_contact',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id')),
    UniqueConstraint('user_id','contact_id')
    )

User_Vehicle = db.Table('user_vehicle',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('vehicle_id', db.Integer, db.ForeignKey('vehicle.id')),
    UniqueConstraint('user_id','vehicle_id')
    )

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(20), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    phone_number = db.Column(db.String(20), unique = True ,nullable = False)
    admin = db.Column(db.Boolean, nullable = False, default = False)
    user_address = db.relationship('Address', secondary = User_Address, backref = 'users' ,lazy = 'dynamic')
    user_contact = db.relationship('Contact', secondary = User_Contact, backref = 'users',lazy = 'dynamic')
    user_vehicle = db.relationship('Vehicle', secondary = User_Vehicle, backref = 'users', lazy = 'dynamic')
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key = True)
    postal_code = db.Column(db.String(10), nullable = False)
    country = db.Column(db.String(20), nullable = False)
    state = db.Column(db.String(20), nullable = False)
    city = db.Column(db.String(20), nullable = False)
    street = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return f"Address('{self.id}', '{self.postal_code}', '{self.country}', '{self.state}', '{self.city}', '{self.street}')"

class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key = True)
    cellphone = db.Column(db.String(20), unique = True, nullable = False)

    def __repr__(self):
        return f"Contact('{self.id}', '{self.cellphone}')"

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key = True)
    plate_number = db.Column(db.String(10), unique = True, nullable = False)
    accelerometer = db.Column(db.String(10), nullable = False , default = '0')
    accidents = db.relationship('Accident', backref = 'vehicles', lazy = 'dynamic')

    def __repr__(self):
        return f"Vehicle('{self.id}','{self.plate_number}', '{self.accelerometer}')"

class Accident(db.Model):
    __tablename__ = 'accident'
    id = db.Column(db.Integer, primary_key = True)
    time_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable = False)
    __table_args__ = (db.UniqueConstraint('time_date', 'vehicle_id'), )

    def __repr__(self):
        return f"Accident('{self.id}', '{self.time_date}','{self.vehicle_id}')"
