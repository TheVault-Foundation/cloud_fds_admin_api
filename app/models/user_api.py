from datetime import datetime

from app.extensions import db


class UserApi(db.Document):
    userId = db.ObjectIdField(required=True)
    apiKey = db.StringField(required=True, unique=True, max_length=100)
    apiSecret = db.StringField(required=True, max_length=300)
    isActive = db.BooleanField(required=True, default=True)
    createdAt = db.DateTimeField(required=True, default=datetime.utcnow)
    createdBy = db.StringField(required=True, max_length=100)
    updatedAt = db.DateTimeField()
    updatedBy = db.StringField(max_length=100)

    meta = {
        'collection': 'userApi',
        'indexes': [
            'userId',
            'apiKey',
            '-createdAt'
        ]
    }
