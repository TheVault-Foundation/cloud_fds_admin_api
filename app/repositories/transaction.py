from bson import ObjectId

from app import models as m
from app.helper import Helper

from ..repositories.user import user_repo


class TransactionRepository(object):
    def get_list(self, args):
        sortable_fields = ['fromAddress', 'fromCurrency', 'toAddress', 'toCurrency', 'senderIp', 'country', 'createdAt']
        page = Helper.get_page_from_args(args)
        size = Helper.get_size_from_args(args)
        optional = args.get('optional')
        sorts = Helper.get_sort_from_args(args, sortable_fields)
        fields = Helper.get_fields_from_args(args)
        user_id = args['user_id']
        username = user_repo.get_by_id(user_id).username
        if sorts is not None:
            args = []
            for sort in sorts:
                column = getattr(m.Transaction, sort[0])
                sort_method = '-' if sort[1] == 'desc' else ''
                args.append(sort_method + column.name)
            if optional is not None and optional == 'all':
                items = m.Transaction.objects(userId=ObjectId(user_id)).order_by(*args)
                page_items = None
                count_items = len(items)
            else:
                transactions = m.Transaction.objects(userId=ObjectId(user_id)).order_by(*args).paginate(page=page, per_page=size)
                items, page_items, count_items = transactions.items, transactions.page, transactions.total
        else:
            transactions = m.Transaction.objects(userId=ObjectId(user_id)).paginate(page=page, per_page=size)
            items, page_items, count_items = transactions.items, transactions.page, transactions.total

        if fields is not None:
            res = []
            for item in items:
                data = {k: item._data[k] for k in item._data if k in fields}
                res.append(data)
        else:
            res = [item._data for item in items]
        res = [{**tx, 'username': username} for tx in res]
        return res, page_items, count_items


tran_repo = TransactionRepository()
