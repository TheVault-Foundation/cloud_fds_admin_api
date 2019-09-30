from datetime import datetime
from app.extensions import db


class UserAccessToken(db.Document):
    userId = db.ObjectIdField(required=True)
    accessToken = db.StringField(required=True, max_length=1000)
    expireAt = db.DateTimeField(required=True)
    CreatedAt = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'userAccessToken',
        'indexes': [
            'userId',
            '-accessToken',
            'expireAt'
        ]
    }
