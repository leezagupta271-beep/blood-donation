def test_create_and_fetch_camp(client, admin_login):
    res_create = client.post('/api/camps', json={
        'name': 'Test Camp',
        'location': 'Downtown Plaza',
        'date': '2026-10-10'
    })
    assert res_create.status_code == 201

    res_fetch = client.get('/api/camps')
    data = res_fetch.get_json()
    assert len(data) >= 1
    found = any(c['name'] == 'Test Camp' for c in data)
    assert found
