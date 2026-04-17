import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Donor, BloodStock, Hospital, BloodRequest, Camp, Registration
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-123'
import os
if os.environ.get('TESTING') == 'True':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    # MySQL DB configuration (Update credentials: username:password@host/db_name)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://avnadmin:<redacted>@mysql-277ebaee-leezagupta271-e93f.d.aivencloud.com:13716/defaultdb?ssl-mode=REQUIRED'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- Template Routes ---
@app.route('/')
def home():
    return render_template('index.html', user=session.get('user_name'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/camps', methods=['GET'])
def camps_page():
    return render_template('camps.html')

@app.route('/availability', methods=['GET'])
def availability_page():
    return render_template('availability.html')

@app.route('/requests', methods=['GET'])
def requests_page():
    return redirect(url_for('needs_page'))

@app.route('/needs', methods=['GET'])
def needs_page():
    return render_template('needs.html')

@app.route('/find_donors', methods=['GET'])
def find_donors_page():
    return render_template('find_donors.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard_page():
    user = User.query.get(session['user_id'])
    if user.role == 'admin':
        return redirect(url_for('admin_page'))
    return render_template('dashboard.html', user=user)

@app.route('/admin', methods=['GET'])
@login_required
def admin_page():
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('dashboard_page'))
    return render_template('admin.html')

@app.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')

# --- API Routes ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    blood_group = data.get('blood_group')
    location = data.get('location')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed_password, role='donor')
    db.session.add(user)
    db.session.commit()

    donor = Donor(user_id=user.id, blood_group=blood_group, phone=phone, location=location)
    db.session.add(donor)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['role'] = user.role
        return jsonify({'message': 'Login successful', 'role': user.role}), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/donors', methods=['GET'])
@login_required
def get_donors():
    donors = Donor.query.join(User).all()
    result = [{
        'id': d.id,
        'name': d.user.name,
        'email': d.user.email,
        'blood_group': d.blood_group,
        'phone': d.phone,
        'location': d.location,
        'last_donation': d.last_donation.strftime('%Y-%m-%d') if d.last_donation else None
    } for d in donors]
    return jsonify(result), 200

@app.route('/api/donors/location/<string:location_query>', methods=['GET'])
def get_donors_by_location(location_query):
    search = f"%{location_query}%"
    donors = Donor.query.join(User).filter(Donor.location.ilike(search)).all()
    if not donors:
        return jsonify([]), 200
    
    result = [{
        'name': d.user.name,
        'blood_group': d.blood_group,
        'phone': d.phone,
        'location': d.location
    } for d in donors]
    return jsonify(result), 200

@app.route('/api/blood_availability', methods=['GET'])
def get_all_availability():
    bg_filter = request.args.get('blood_group')
    query = BloodStock.query.join(Hospital)
    if bg_filter and bg_filter != 'all':
        query = query.filter(BloodStock.blood_group == bg_filter)
    
    stock = query.all()
    result = [{
        'hospital': s.hospital.name,
        'location': s.hospital.location,
        'contact': s.hospital.contact,
        'blood_group': s.blood_group,
        'units_available': s.units_available,
        'last_updated': s.last_updated.strftime('%Y-%m-%d %H:%M:%S') if s.last_updated else None
    } for s in stock]
    return jsonify(result), 200

@app.route('/api/update_stock', methods=['POST'])
@login_required
def update_stock():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    hospital_id = data.get('hospital_id')
    blood_group = data.get('blood_group')
    units = data.get('units')
    action = data.get('action') # 'add' or 'remove'
    
    stock = BloodStock.query.filter_by(hospital_id=hospital_id, blood_group=blood_group).first()
    if not stock:
        if action == 'add':
            stock = BloodStock(hospital_id=hospital_id, blood_group=blood_group, units_available=units)
            db.session.add(stock)
        else:
            return jsonify({'error': 'Invalid stock record'}), 400
    else:
        if action == 'add':
            stock.units_available += units
        elif action == 'remove' and stock.units_available >= units:
            stock.units_available -= units
        else:
            return jsonify({'error': 'Not enough units available'}), 400
        
    db.session.commit()
    return jsonify({'message': 'Stock updated successfully', 'current_stock': stock.units_available}), 200

@app.route('/api/hospitals', methods=['GET', 'POST'])
@login_required
def manage_hospitals():
    if request.method == 'GET':
        hospitals = Hospital.query.all()
        return jsonify([{'id': h.id, 'name': h.name, 'location': h.location} for h in hospitals]), 200
    
    if request.method == 'POST':
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        hospital = Hospital(name=data['name'], location=data.get('location'), contact=data.get('contact'))
        db.session.add(hospital)
        db.session.commit()
        return jsonify({'message': 'Hospital added successfully'}), 201

@app.route('/api/blood_requests/pending', methods=['GET'])
def get_pending_requests():
    requests = BloodRequest.query.join(Hospital).filter(BloodRequest.status == 'pending').all()
    urgency_order = {'high': 1, 'medium': 2, 'low': 3}
    requests = sorted(requests, key=lambda r: urgency_order.get(r.urgency, 2))
    return jsonify([{
        'id': r.id,
        'hospital': r.hospital.name,
        'location': r.hospital.location,
        'contact': r.hospital.contact,
        'blood_group': r.blood_group,
        'units': r.units_required,
        'urgency': r.urgency,
        'status': r.status,
        'date': r.request_date.strftime('%Y-%m-%d')
    } for r in requests]), 200

@app.route('/api/blood_requests', methods=['GET'])
def get_blood_requests():
    requests = BloodRequest.query.join(Hospital).filter(BloodRequest.status == 'pending').all()
    urgency_order = {'high': 1, 'medium': 2, 'low': 3}
    requests = sorted(requests, key=lambda r: urgency_order.get(r.urgency, 2))
    return jsonify([{
        'id': r.id,
        'hospital': r.hospital.name,
        'blood_group': r.blood_group,
        'units': r.units_required,
        'urgency': r.urgency,
        'status': r.status,
        'date': r.request_date.strftime('%Y-%m-%d')
    } for r in requests]), 200
        
@app.route('/api/blood_request', methods=['POST'])
@login_required
def create_blood_request():
    data = request.json
    hospital_id = data.get('hospital_id')
    blood_group = data.get('blood_group')
    units = data.get('units')
    urgency = data.get('urgency', 'medium')
    
    req = BloodRequest(hospital_id=hospital_id, blood_group=blood_group, units_required=units, urgency=urgency)
    db.session.add(req)
    db.session.commit()
    return jsonify({'message': 'Request created successfully'}), 201

@app.route('/api/blood_request/<int:req_id>/approve', methods=['POST'])
@login_required
def approve_request(req_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    req = BloodRequest.query.get_or_404(req_id)
    if req.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400
        
    global_stock = BloodStock.query.filter(BloodStock.blood_group==req.blood_group, BloodStock.units_available >= req.units_required).first()
    if global_stock:
        global_stock.units_available -= req.units_required
        req.status = 'completed'
        db.session.commit()
        return jsonify({'message': f'Request approved using {global_stock.hospital.name} stock'}), 200
    
    return jsonify({'error': 'Insufficient stock across all banks'}), 400

@app.route('/api/camps', methods=['GET', 'POST'])
def manage_camps():
    if request.method == 'GET':
        camps = Camp.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'location': c.location,
            'date': c.date.strftime('%Y-%m-%d')
        } for c in camps]), 200
        
    if request.method == 'POST':
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        camp_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        camp = Camp(name=data['name'], location=data['location'], date=camp_date)
        db.session.add(camp)
        db.session.commit()
        return jsonify({'message': 'Camp added successfully'}), 201

@app.route('/api/register_camp', methods=['POST'])
@login_required
def register_camp():
    data = request.json
    camp_id = data.get('camp_id')
    
    user = User.query.get(session['user_id'])
    if user.role != 'donor':
        return jsonify({'error': 'Only donors can register for camps'}), 403
        
    donor = Donor.query.filter_by(user_id=user.id).first()
    
    if Registration.query.filter_by(donor_id=donor.id, camp_id=camp_id).first():
        return jsonify({'error': 'Already registered for this camp'}), 400
        
    reg = Registration(donor_id=donor.id, camp_id=camp_id)
    db.session.add(reg)
    db.session.commit()
    return jsonify({'message': 'Successfully registered for camp'}), 201

@app.route('/api/donate', methods=['POST'])
@login_required
def record_donation():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    donor_id = data.get('donor_id')
    
    donor = Donor.query.get_or_404(donor_id)
    donor.last_donation = datetime.date.today()
    
    stock = BloodStock.query.filter_by(hospital_id=1, blood_group=donor.blood_group).first()
    if stock:
        stock.units_available += 1
    else:
        stock = BloodStock(hospital_id=1, blood_group=donor.blood_group, units_available=1)
        db.session.add(stock)
        
    db.session.commit()
    return jsonify({'message': 'Donation recorded and stock updated'}), 200

@app.route('/api/dashboard_stats', methods=['GET'])
@login_required
def dashboard_stats():
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        total_donors = Donor.query.count()
        active_camps = Camp.query.filter(Camp.date >= datetime.date.today()).count()
        total_inventory = db.session.query(db.func.sum(BloodStock.units_available)).scalar() or 0
        
        most_demanded_query = db.session.query(BloodRequest.blood_group, db.func.sum(BloodRequest.units_required)).filter(BloodRequest.status == 'pending').group_by(BloodRequest.blood_group).order_by(db.func.sum(BloodRequest.units_required).desc()).first()
        most_demanded = most_demanded_query[0] if most_demanded_query else "N/A"
        
        pending_requests = BloodRequest.query.filter_by(status='pending').count()
        
        return jsonify({
            'total_donors': total_donors,
            'active_camps': active_camps,
            'total_inventory': int(total_inventory),
            'pending_requests': pending_requests,
            'most_demanded': most_demanded
        }), 200
        
    elif user.role == 'donor':
        donor = Donor.query.filter_by(user_id=user.id).first()
        donations = 0 # Can be calculated based on historical records if table existed
        if donor.last_donation:
            next_eligible = donor.last_donation + datetime.timedelta(days=90)
            eligible_str = next_eligible.strftime('%b %d, %Y')
        else:
            eligible_str = 'Currently Eligible'
            
        camps_registered = len(donor.registrations)
        return jsonify({
            'donations': donations,
            'lives_saved': donations * 3,
            'next_eligible': eligible_str,
            'camps_registered': camps_registered,
            'blood_group': donor.blood_group
        }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
