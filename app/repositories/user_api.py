from datetime import datetime

from bson import ObjectId
from flask import current_app

from app import models as m
from app.helper import Helper


class UserAPIRepository(object):
    def get_list(self, args):
        sortable_fields = ['createdAt', 'createdBy', 'updatedAt', 'updatedBy', 'isActive']
        page = Helper.get_page_from_args(args)
        size = Helper.get_size_from_args(args)
        optional = args.get('optional')
        sorts = Helper.get_sort_from_args(args, sortable_fields)
        fields = Helper.get_fields_from_args(args)
        user_id = args['user_id']
        if sorts is not None:
            args = []
            for sort in sorts:
                column = getattr(m.UserApi, sort[0])
                sort_method = '-' if sort[1] == 'desc' else ''
                args.append(sort_method + column.name)
            if optional is not None and optional == 'all':
                items = m.UserApi.objects(userId=ObjectId(user_id)).order_by(*args)
                page_items = None
                count_items = None
            else:
                user_apis = m.UserApi.objects(userId=ObjectId(user_id)).order_by(*args).paginate(page=page, per_page=size)
                items, page_items, count_items = user_apis.items, user_apis.page, user_apis.total
        if fields is not None:
            res = []
            for item in items:
                data = {k: item._data[k] for k in item._data if k in fields}
                res.append(data)
        else:
            res = [item._data for item in items]
        return res, page_items, count_items

    def create(self, data, current_user):
        data['updatedAt'] = datetime.utcnow()
        data['createdBy'] = current_user.username
        data['userId'] = ObjectId(data['userId'])
        user_api = m.UserApi(**data)
        user_api.save()
        return user_api

    def get_by_id(self, api_id):
        return m.UserApi.objects(id=ObjectId(api_id)).first()

    def update(self, user_api, current_user, args):
        args['updatedAt'] = datetime.utcnow()
        args['updatedBy'] = current_user.username
        try:
            user_api.update(**args)
            user_api.reload()
            return user_api
        except Exception as e:
            current_app.logger.error('exception on user_api update:', e)
            user_api.reload()
            return user_api


user_api_repo = UserAPIRepository()
