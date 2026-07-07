from app import create_app
from models import db

app = create_app()
with app.app_context():
    client = app.test_client()
    r = client.post('/api/auth/login', json={'username':'admin','password':'admin123','role':'admin'})
    print('admin login', r.status_code, r.get_json())
    token = r.get_json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    r = client.post('/api/admin/doctors', json={'username':'doc1','password':'docpass','name':'John Doe','specialization':'Cardiology'}, headers=headers)
    print('create doctor', r.status_code, r.get_json())
    r = client.get('/api/admin/doctors', headers=headers)
    print('list doctors', r.status_code, r.get_json())
    r = client.post('/api/auth/register/patient', json={'username':'pat1','password':'patpass','name':'Alice','age':30,'contact':'12345'})
    print('register patient', r.status_code, r.get_json())
    r = client.post('/api/auth/login', json={'username':'pat1','password':'patpass','role':'patient'})
    print('patient login', r.status_code, r.get_json())
    ptoken = r.get_json().get('access_token')
    ph = {'Authorization': f'Bearer {ptoken}'}
    docs = client.get('/api/admin/doctors', headers=headers).get_json()
    did = docs[0]['id'] if docs else None
    r = client.post('/api/patient/appointments', json={'doctor_id': did,'datetime':'2025-01-01T10:00:00Z'}, headers=ph)
    print('book appt', r.status_code, r.get_json())
    r = client.get('/api/patient/history', headers=ph)
    print('history', r.status_code, r.get_json())
