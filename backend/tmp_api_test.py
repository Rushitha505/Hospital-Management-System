import requests
base='http://127.0.0.1:5000/api'
res=requests.post(base+'/auth/login', json={'username':'admin','password':'admin123','role':'admin'})
print('admin login', res.status_code, res.text)
if res.status_code==200:
    token=res.json()['access_token']
    r2=requests.get(base+'/admin/doctors', headers={'Authorization':f'Bearer {token}'})
    print('get doctors', r2.status_code, r2.text)
