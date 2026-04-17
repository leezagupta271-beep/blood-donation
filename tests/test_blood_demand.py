def test_create_and_fetch_request(client, admin_login):
    # Create request
    res_create = client.post('/api/blood_request', json={
        'hospital_id': 1,
        'blood_group': 'B+',
        'units': 2,
        'urgency': 'high'
    })
    assert res_create.status_code == 201

    # Fetch pending requests
    res_fetch = client.get('/api/blood_requests/pending')
    data = res_fetch.get_json()
    
    assert len(data) >= 1
    found = any(req['blood_group'] == 'B+' and req['urgency'] == 'high' for req in data)
    assert found

def test_approve_request_sufficient_stock(client, admin_login):
    client.post('/api/blood_request', json={
        'hospital_id': 1,
        'blood_group': 'A+', # We have 10 units via fixture
        'units': 5,
        'urgency': 'medium'
    })
    
    res_fetch = client.get('/api/blood_requests/pending')
    reqs = res_fetch.get_json()
    new_req = next((r for r in reqs if r['blood_group'] == 'A+' and r['units'] == 5), None)
    assert new_req is not None
    
    res_appr = client.post(f'/api/blood_request/{new_req["id"]}/approve')
    assert res_appr.status_code == 200
    assert b'approved using' in res_appr.data
    
    # Check stock depleted
    stock_res = client.get('/api/blood_availability?blood_group=A%2B')
    assert stock_res.get_json()[0]['units_available'] == 5

def test_approve_request_insufficient_stock(client, admin_login):
    client.post('/api/blood_request', json={
        'hospital_id': 1,
        'blood_group': 'O-', # We only have 5 units
        'units': 10,
        'urgency': 'high'
    })
    
    res_fetch = client.get('/api/blood_requests/pending')
    reqs = res_fetch.get_json()
    new_req = next((r for r in reqs if r['blood_group'] == 'O-' and r['units'] == 10), None)
    
    res_appr = client.post(f'/api/blood_request/{new_req["id"]}/approve')
    assert res_appr.status_code == 400
    assert b'Insufficient stock' in res_appr.data
