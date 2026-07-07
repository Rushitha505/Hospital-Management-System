import requests, datetime
base='http://127.0.0.1:5000/api'

# Admin login
admin = requests.post(base+'/auth/login', json={'username':'admin','password':'admin123','role':'admin'})
print('admin login', admin.status_code)
admin_token = admin.json()['access_token'] if admin.status_code==200 else None
headers = {'Authorization': f'Bearer {admin_token}'}

# Create doctor
create_doc = requests.post(base+'/admin/doctors', json={'username':'doc1','password':'docpass','name':'Dr Test','specialization':'General','schedule':'{}'}, headers=headers)
print('create doctor', create_doc.status_code, create_doc.text)

# Register patient
register = requests.post(base+'/auth/register/patient', json={'username':'pat1','password':'patpass','name':'Pat Test','age':28,'contact':'12345'})
print('register patient', register.status_code, register.text)

# Patient login
patient_login = requests.post(base+'/auth/login', json={'username':'pat1','password':'patpass','role':'patient'})
print('patient login', patient_login.status_code, patient_login.text)
pat_token = patient_login.json().get('access_token') if patient_login.status_code==200 else None

# Doctor login
doctor_login = requests.post(base+'/auth/login', json={'username':'doc1','password':'docpass','role':'doctor'})
print('doctor login', doctor_login.status_code, doctor_login.text)
doc_token = doctor_login.json().get('access_token') if doctor_login.status_code==200 else None

# Doctor set availability tomorrow
if doc_token:
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    avail = requests.post(base+'/doctor/availability', json={'date': tomorrow, 'is_available': True}, headers={'Authorization': f'Bearer {doc_token}'})
    print('doctor availability', avail.status_code, avail.text)

# Patient search doctors
if pat_token:
    doctors = requests.get(base+'/patient/doctors', headers={'Authorization': f'Bearer {pat_token}'})
    print('patient doctors', doctors.status_code, doctors.text[:500])

# Patient book appointment tomorrow at 10am
if pat_token:
    dt = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1), datetime.time(10,0)).isoformat()
    book = requests.post(base+'/patient/appointments', json={'doctor_id': 1, 'datetime': dt}, headers={'Authorization': f'Bearer {pat_token}'})
    print('book appointment', book.status_code, book.text)

# Doctor get appointments
if doc_token:
    appts = requests.get(base+'/doctor/appointments', headers={'Authorization': f'Bearer {doc_token}'})
    print('doctor appointments', appts.status_code, appts.text)
