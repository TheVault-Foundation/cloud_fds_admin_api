from app.extensions import db


class ApiUsageCount(db.Document):
    apiId = db.ObjectIdField(required=True)
    year = db.IntField(required=True)
    month = db.IntField(required=True)
    count = db.IntField(required=True, default=0)

    meta = {
        'collection': 'apiUsageCount',
        'indexes': [
            'apiId',
            '-year',
            '-month'
        ]
    }
