from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='donor')

class Donor(db.Model):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    location = db.Column(db.String(255))
    last_donation = db.Column(db.Date, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('donor_profile', uselist=False))
    registrations = db.relationship('Registration', backref='donor', cascade='all, delete-orphan')

class BloodStock(db.Model):
    __tablename__ = 'blood_stock'
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255))
    contact = db.Column(db.String(50))
    requests = db.relationship('BloodRequest', backref='hospital', cascade='all, delete-orphan')
    blood_stocks = db.relationship('BloodStock', backref='hospital', cascade='all, delete-orphan')

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_required = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending') # pending, completed, rejected
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

class Camp(db.Model):
    __tablename__ = 'camps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    registrations = db.relationship('Registration', backref='camp', cascade='all, delete-orphan')

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'), nullable=False)
    camp_id = db.Column(db.Integer, db.ForeignKey('camps.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
