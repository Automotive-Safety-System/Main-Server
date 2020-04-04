from gradproj import app, db, mail
from flask import url_for
from flask_mail import Message
from gradproj.models import User


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset Request',
                  sender='Safetysystemzu@gmail.com',
                  recipients=[user.email])
    msg.body = f''' to reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this mail and no changes will me made.
'''
    mail.send(msg)
