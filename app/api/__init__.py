
from flask import Blueprint
from flask_restplus import Api

from app.api.password import ns as password_ns
from app.api.user import ns as user_ns

bp = Blueprint('api', __name__, url_prefix='/v1/admin')

api = Api(bp, version=1.0, title='CloudFDS Admin API', description='CloudFDS Admin API', doc='/doc/')

api.add_namespace(ns=user_ns)
api.add_namespace(ns=password_ns)


@bp.before_app_first_request
def before_app_first_request():
    from app.repositories.billing_type import billing_type_repo
    if billing_type_repo.get_by_billing_type('Monthly') is None:
        billing_type_repo.create({'billingType': 'Monthly'})
    if billing_type_repo.get_by_billing_type('Metered') is None:
        billing_type_repo.create({'billingType': 'Metered'})
