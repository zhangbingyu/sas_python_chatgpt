from datetime import datetime
from enum import Enum
from sre_constants import SUCCESS

from flask_login import UserMixin

from app import db

class TransactionStatus(Enum):
    FAILED = 0
    COMPLETION = 1

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), unique = True, index = True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    date_joined = db.Column(db.DateTime(), default = datetime.utcnow)
    active = db.Column(db.Boolean)
    credit = db.Column(db.Integer)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_order = db.Column(db.DateTime(), default = datetime.utcnow)
    input_token = db.Column(db.Integer)
    output_token = db.Column(db.Integer)
    status = db.Column(db.Enum(TransactionStatus), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
