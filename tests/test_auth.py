def test_user_registration(client):
    response = client.post('/api/register', json={
        'name': 'John Doe',
        'email': 'john@test.com',
        'phone': '1234567890',
        'blood_group': 'A+',
        'location': 'New York',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert b'Registration successful' in response.data

def test_duplicate_registration(client):
    # First registration
    client.post('/api/register', json={
        'name': 'John Doe',
        'email': 'john@test.com',
        'phone': '1234567890',
        'blood_group': 'A+',
        'location': 'New York',
        'password': 'password123'
    })
    # Duplicate email attempt
    response = client.post('/api/register', json={
        'name': 'Jane Doe',
        'email': 'john@test.com',
        'phone': '0987654321',
        'blood_group': 'B+',
        'location': 'Boston',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert b'Email already exists' in response.data

def test_login_success(client):
    # Register first
    client.post('/api/register', json={
        'name': 'Alice',
        'email': 'alice@test.com',
        'phone': '111',
        'blood_group': 'O+',
        'password': 'mypassword'
    })
    
    # Login
    response = client.post('/api/login', json={
        'email': 'alice@test.com',
        'password': 'mypassword'
    })
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_login_failure(client):
    response = client.post('/api/login', json={
        'email': 'nonexistent@test.com',
        'password': 'wrong'
    })
    assert response.status_code == 401
    assert b'Invalid email or password' in response.data
