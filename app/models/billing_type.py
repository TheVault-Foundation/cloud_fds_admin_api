from app.extensions import db


class BillingType(db.Document):
    billingType = db.StringField(required=True, regex=r'^(Monthly|Metered)$', unique=True)

    meta = {'collection': 'billingType'}
