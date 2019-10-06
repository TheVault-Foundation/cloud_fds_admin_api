from datetime import datetime

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

    @staticmethod
    def increaseCount(apiId):
        curUtc = datetime.utcnow()

        year = curUtc.year
        month = curUtc.month

        ApiUsageCount.objects(apiId=apiId, year=year, month=month).update_one(inc__count=1, upsert=True)
