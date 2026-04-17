def test_get_availability_all(client):
    response = client.get('/api/blood_availability')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2 # Setup created A+ and O- instances
    
def test_filter_availability(client):
    # Filter A+
    valid_res = client.get('/api/blood_availability?blood_group=A%2B')
    valid_data = valid_res.get_json()
    assert len(valid_data) == 1
    assert valid_data[0]['blood_group'] == 'A+'
    assert valid_data[0]['units_available'] == 10

    # Filter invalid BG
    invalid_res = client.get('/api/blood_availability?blood_group=AB-')
    assert len(invalid_res.get_json()) == 0

def test_admin_add_stock(client, admin_login):
    # Admin is logged in via fixture
    response = client.post('/api/update_stock', json={
        'hospital_id': 1,
        'blood_group': 'B+',
        'units': 20,
        'action': 'add'
    })
    assert response.status_code == 200
    assert response.get_json()['current_stock'] == 20

def test_admin_remove_stock(client, admin_login):
    response = client.post('/api/update_stock', json={
        'hospital_id': 1,
        'blood_group': 'A+',
        'units': 5,
        'action': 'remove'
    })
    assert response.status_code == 200
    assert response.get_json()['current_stock'] == 5

def test_unauthorized_stock_update(client):
    response = client.post('/api/update_stock', json={
        'hospital_id': 1,
        'blood_group': 'A+',
        'units': 5,
        'action': 'add'
    })
    assert response.status_code == 401 # Should block unauthenticated usage
