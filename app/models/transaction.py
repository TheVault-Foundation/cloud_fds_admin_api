from datetime import datetime
from app.extensions import db


class Transaction(db.Document):
    userId = db.ObjectIdField(required=True)
    fromAddress = db.StringField(required=True, max_length=200)
    fromCurrency = db.StringField(required=True, max_length=20)
    toAddress = db.StringField(required=True, max_length=200)
    toCurrency = db.StringField(required=True, max_length=20)
    amount = db.DecimalField(required=True, precision=10)
    senderDeviceId = db.IntField(required=False)
    senderIp = db.StringField(required=False, max_length=20)
    country = db.StringField(required=False, max_length=20)
    transactedAt = db.DateTimeField(required=False)  # StringField(required=False, max_length=15)
    score = db.DecimalField(required=True, default=0)
    txHash = db.StringField(required=False, max_length=200)
    createdAt = db.DateTimeField(default=datetime.utcnow)
    updatedAt = db.DateTimeField()
    updatedBy = db.StringField(max_length=100)

    meta = {
        'collection': 'transactions',
        'indexes': [
            'userId',
            'fromAddress',
            'fromCurrency',
            '-transactedAt',
            '-createdAt',
            'score'
        ]
    }
