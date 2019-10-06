from bson import ObjectId

from app import models as m
from app.helper import Helper


class ApiUsageCountRepository(object):
    def get_list(self, args):
        user_id = args['user_id']
        user_apis = m.UserApi.objects(userId=ObjectId(user_id))
        api_ids = [user_api.id for user_api in user_apis]
        sortable_fields = ['apiId', 'year', 'month', 'count']
        page = Helper.get_page_from_args(args)
        size = Helper.get_size_from_args(args)
        optional = args.get('optional')
        sorts = Helper.get_sort_from_args(args, sortable_fields)
        fields = Helper.get_fields_from_args(args)
        if sorts:
            args = []
            for sort in sorts:
                column = getattr(m.ApiUsageCount, sort[0])
                sort_method = '-' if sort[1] == 'desc' else ''
                args.append(sort_method + column.name)
            if optional is not None and optional == 'all':
                items = m.ApiUsageCount.objects(apiId__in=api_ids).order_by(*args)
                page_items = None
                count_items = len(items)
            else:
                api_usage_counts = m.ApiUsageCount.objects(apiId__in=api_ids).order_by(*args).paginate(page=page, per_page=size)
                items, page_items, count_items = api_usage_counts.items, api_usage_counts.page, api_usage_counts.total
        else:
            api_usage_counts = m.ApiUsageCount.objects(apiId__in=api_ids).paginate(page=page, per_page=size)
            items, page_items, count_items = api_usage_counts.items, api_usage_counts.page, api_usage_counts.total
        res = []
        for item in items:
            data = {k: item._data[k] for k in item._data if fields is None or k in fields}
            res.append(data)
        return res, page_items, count_items

    def get_by_id(self, api_id):
        return m.ApiUsageCount.objects(apiId=ObjectId(api_id))


api_usage_count_repo = ApiUsageCountRepository()
