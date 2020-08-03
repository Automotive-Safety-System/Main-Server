from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from gradproj import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# get user by ID docerator 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


User_Contact = db.Table('user_contact',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('contact_id', db.Integer, db.ForeignKey('contact.id')),
                        UniqueConstraint('user_id', 'contact_id')
                        )

User_Vehicle = db.Table('user_vehicle',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('vehicle_id', db.Integer, db.ForeignKey('vehicle.id')),
                        UniqueConstraint('user_id', 'vehicle_id')
                        )

observation = db.Table('observers', db.Model.metadata,
                       db.Column('observation_id', db.SMALLINT, primary_key=True),
                       db.Column('observer_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('observed_id', db.Integer, db.ForeignKey('user.id')),
                       UniqueConstraint('observer_id', 'observed_id'))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String, nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    user_contact = db.relationship('Contact', secondary=User_Contact, backref='users', lazy='dynamic')
    user_vehicle = db.relationship('Vehicle', secondary=User_Vehicle, backref='users', lazy='dynamic')
    observers = db.relationship(
        'User',
        secondary=observation,
        primaryjoin=id == observation.c.observer_id,
        secondaryjoin=id == observation.c.observed_id,
        backref=db.backref('observation')
    )

    def equals(self, user):
        if self.email == user.email:
            return True

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        print(s)
        try:
            user_id = s.loads(token)['user_id']
            print(user_id)
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    street = db.Column(db.String(20), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    users = db.relationship("User", backref='address', lazy=True)
    db.UniqueConstraint(country, state, city, street, postal_code)

    def __repr__(self):
        return f"Address('{self.id}', '{self.postal_code}', '{self.country}', '{self.state}', '{self.city}', '{self.street}')"

    def equals(self, address):
        if self.country == address.country \
                and self.state == address.state \
                and self.city == address.city \
                and self.street == address.street \
                and self.postal_code == address.postal_code:
            return True


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    cellphone = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"Contact('{self.id}', '{self.cellphone}')"


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String, nullable=False, default="Parked")
    accelerometer = db.Column(db.String(10), nullable=False, default='0')
    vehicle_model = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    update_date = db.Column(db.Date, nullable=False, default=datetime.today())
    accidents = db.relationship('Accident', backref='vehicles', lazy='dynamic')

    def __repr__(self):
        return f"Vehicle('{self.id}','{self.plate_number}', '{self.accelerometer}')"


class Accident(db.Model):
    __tablename__ = 'accident'
    id = db.Column(db.Integer, primary_key=True)
    time_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String, nullable=False)
    accelerometer = db.Column(db.String(10), nullable=False, default='0')
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    db.UniqueConstraint(vehicle_id, location, time_date)

    def __repr__(self):
        return f"Accident('{self.id}', '{self.time_date}','{self.vehicle_id}')"
