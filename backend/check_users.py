from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['pixel_pirates']
for u in db.users.find({}, {'email':1, 'password':1, '_id':0}):
    pwd = u.get('password','')
    email = u.get('email','')
    print(f'{email}: len={len(pwd)}, starts={pwd[:20]}...')
