import os
import sys
import pytest
from datetime import datetime, date

os.environ['TESTING'] = 'True'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from app import db
from models import User, Hospital, BloodStock, BloodRequest, Camp, Donor
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost'
    })
    
    with flask_app.app_context():
        db.create_all()
        
        # Setup basic data for testing
        admin_pw = generate_password_hash('admin123')
        test_admin = User(name='Admin Test', email='admin@test.com', password=admin_pw, role='admin')
        db.session.add(test_admin)
        
        test_hospital = Hospital(name='Test Bank', location='Test City', contact='123456')
        db.session.add(test_hospital)
        
        db.session.commit()
        
        # Add basic blood stock to hospital id 1
        stock_A = BloodStock(hospital_id=1, blood_group='A+', units_available=10)
        stock_O = BloodStock(hospital_id=1, blood_group='O-', units_available=5)
        db.session.add_all([stock_A, stock_O])
        db.session.commit()

        yield flask_app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_login(client):
    return client.post('/api/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
