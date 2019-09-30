from datetime import datetime

from app.extensions import db


class User(db.Document):
    username = db.StringField(required=True, unique=True, max_length=100)
    password = db.StringField(required=True, max_length=100)
    company = db.StringField(max_length=100)
    email = db.StringField(required=True, max_length=100)
    contactNumber = db.StringField(max_length=100)
    address = db.StringField(max_length=200)
    billingType = db.ObjectIdField()
    emailVerified = db.BooleanField(required=True, default=False)
    roleType = db.StringField(required=True, default="User", regex=r'^(Admin|User)$')
    isActive = db.BooleanField(required=True, default=True)
    lastSignin = db.DateTimeField()
    createdAt = db.DateTimeField(required=True, default=datetime.utcnow)
    createdBy = db.StringField(required=True)
    updatedAt = db.DateTimeField()
    updatedBy = db.StringField(max_length=100)

    meta = {
        'collection': 'user',
        'indexes': [
            'username',
            'email',
            '-createdAt'
        ]
    }
