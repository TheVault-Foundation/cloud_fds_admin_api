from app.extensions import db
from mongoengine import queryset_manager


class DeviceType(db.Document):
    deviceId = db.IntField(required=True)
    deviceType = db.StringField(required=True, max_length=50)

    meta = {'collection': 'deviceType'}

    @queryset_manager
    def objects(doc_cls, queryset):  # noqa
        return queryset.order_by('deviceId')
