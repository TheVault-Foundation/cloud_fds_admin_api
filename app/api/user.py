import os
from uuid import uuid4

from flask import current_app, render_template, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,  # noqa
                                jwt_required, jwt_optional)
from flask_restplus import Namespace, Resource
from flask import redirect

from app.email import send_email
from app.errors.exceptions import BadRequest, NotFound
from app.extensions import flask_bcrypt
from app.repositories.transaction import tran_repo
from app.repositories.user import user_repo
from app.repositories.user_access_token import user_access_token_repo
from app.repositories.user_api import user_api_repo
from app.repositories.billing_type import billing_type_repo
from app.repositories.api_usage_count import api_usage_count_repo

from ..decorators import authorized, consumes, use_args
from ..utils import to_json

ns = Namespace(name="users", description="Users related operation")


@ns.route('/verify')
class APIUserEmailRegistration(Resource):
    def get(self):
        args = request.args.to_dict()
        token = args.get('token')
        if token is not None:
            user, message = user_repo.get_user_from_token_registration(token=token)
            if message:
                verify = "false"
            else:
                user = user_repo.verify_user(user)
                verify = "true"
        else:
            verify = "false"
        return redirect("{url}?verify={verify}".format(url=current_app.config.get('LOGIN_URL'), verify=verify))


@ns.route('/<string:user_id>')
class APIUser(Resource):

    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'password': {'type': 'string'},
            'company': {'type': 'string'},
            'contactNumber': {'type': 'string'},
            'address': {'type': 'string'},
            'isActive': {'type': 'boolean'},
            'roleType': {'type': 'string', 'enum': ['Admin', 'User']}
        },
    })
    def put(self, current_user, args, user_id):
        if current_user.roleType == 'User' and (str(current_user.id != user_id) or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        if current_user.roleType == 'User':
            del args['isActive']
            del args['roleType']
        user = user_repo.get_by_id(user_id)
        if user is None:
            raise NotFound(message='User is not found')
        user = user_repo.update_user(user, current_user, args)
        return {'item': to_json(user._data)}, 204

    @jwt_required
    @authorized()
    def get(self, current_user, user_id):
        if current_user.roleType == 'User' and (str(current_user.id) != user_id or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        user = user_repo.get_by_id(user_id)
        if user is None:
            raise NotFound(message='User is not found')
        data = {k: user._data[k] for k in user._data if k != 'password'}
        return {'item': to_json(data)}, 200


@ns.route('/<string:user_id>/usage')
class APIUsageDetail(Resource):
    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'page': {'type': 'string'},
            'size': {'type': 'string'},
            'sort': {'type': 'string'},
            'filter': {'type': 'string'},
            'optional': {'type': 'string'}
        }
    })
    def get(self, current_user, args, user_id):
        if current_user.roleType == 'User' and (str(current_user.id) != user_id or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        args['user_id'] = user_id
        items, page_items, count_items = api_usage_count_repo.get_list(args)
        res = [to_json(item) for item in items]
        return {'items': res, 'page': page_items, 'count': count_items}, 200


@ns.route('/<string:user_id>/transactions')
class APITransactionList(Resource):

    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'page': {'type': 'string'},
            'size': {'type': 'string'},
            'sort': {'type': 'string'},
            'filter': {'type': 'string'},
            'optional': {'type': 'string'}
        }
    })
    def get(self, current_user, args, user_id):
        if current_user.roleType == 'User' and (str(current_user.id) != user_id or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        args['user_id'] = user_id
        items, page_items, count_items = tran_repo.get_list(args)
        res = [to_json(item) for item in items]
        return {'items': res, 'page': page_items, 'count': count_items}, 200


@ns.route('/<string:user_id>/userapi')
class APIUserAPIListAndCreate(Resource):

    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'page': {'type': 'string'},
            'size': {'type': 'string'},
            'sort': {'type': 'string'},
            'filter': {'type': 'string'},
            'optional': {'type': 'string'},
            'active': {'type': 'string'},
        }
    })
    def get(self, current_user, args, user_id):
        if args.get('active') == 'false':
            active = False
        elif args.get('active') == 'true':
            active = True
        else:
            active = None
        if current_user.roleType == 'User' and (str(current_user.id) != user_id or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        args['user_id'] = user_id
        items, page_items, count_items = user_api_repo.get_list(args, active)
        res = [to_json(item) for item in items]
        return {'items': res, 'page': page_items, 'count': count_items}, 200

    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'apiName': {'type': 'string'}
        }
    })
    def post(self, current_user, args, user_id):
        args['apiKey'] = uuid4().hex
        args['apiSecret'] = os.urandom(32).hex()
        args['userId'] = user_id
        user = user_api_repo.create(args, current_user)
        return {'item': to_json(user._data), 'message': 'create UserAPI successfully'}, 200


@ns.route('/<string:user_id>/userapi/<string:api_id>')
class APIUserAPIUpdate(Resource):
    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'isActive': {'type': 'boolean'},
            'apiName': {'type': 'string'}
        }
    })
    def put(self, current_user, args, user_id, api_id):
        if current_user.roleType == 'User':
            raise BadRequest(message='RoleType is not valid')
        user_api = user_api_repo.get_by_id(api_id)
        if user_api is None:
            raise NotFound(message='UserAPI is not found')
        if str(user_api.userId) != user_id:
            raise BadRequest(message='api_id is not valid')
        user_api = user_api_repo.update(user_api, current_user, args)
        return {'item': to_json(user_api._data)}, 204


@ns.route('')
class APIUserRegisterAndList(Resource):
    @jwt_optional
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'maxLength': 128},
            'password': {'type': 'string'},
            'company': {'type': 'string'},
            'createdBy': {'type': 'string'},
            'email': {
                'type': 'string',
                'format': 'email'
            },
            'address': {'type': 'string'},
            'roleType': {'type': 'string', "enum": ['Admin', 'User']},
            'contactNumber': {
                'type': 'string',
            },
            'billingType': {'type': 'string', 'enum': ['Monthly', 'Metered']}
        },
        'required': ['email', 'password']
    })
    def post(self, current_user, args):
        ''' register user endpoint '''
        role_type = args.get('roleType', 'User')
        if role_type not in ['Admin', 'User']:
            raise BadRequest(message='Role type must be Admin or User')
        billing_type = args.get('billingType', 'Monthly')
        if billing_type not in ['Monthly', 'Metered']:
            raise BadRequest(message='Billing type must be Monthly or Metered')
        args['billingType'] = billing_type_repo.get_by_billing_type(billing_type).id
        args['roleType'] = role_type
        created_by = args.get('username') if current_user is None else current_user.username
        args['createdBy'] = args.get('createdBy', created_by)
        if 'username' not in args and 'email' not in args:
            raise BadRequest(code=400, message='Username or email must be required')
        args['password'] = flask_bcrypt.generate_password_hash(args['password'])

        user, message = user_repo.insert_one(args)
        if user is None:
            raise BadRequest(code=400, message=message)
        token = user_repo.generate_registration_token(user)
        url = "{path}/v1/admin/users/verify?token={token}".format(path=current_app.config.get('API_URL'), token=token)
        send_email(
            subject='[TheVault] Email Registration',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email],
            html_body=render_template('email/email_verification.html', user=user, url=url))
        data = user._data
        del data['password']
        return {'item': to_json(data), 'message': 'Signup user is successful'}, 201

    @jwt_required
    @authorized()
    @use_args(**{
        'type': 'object',
        'properties': {
            'page': {'type': 'string'},
            'size': {'type': 'string'},
            'sort': {'type': 'string'},
            'filter': {'type': 'string'},
            'optional': {'type': 'string'},
        }
    })
    def get(self, current_user, args):
        if current_user.roleType == 'User':
            raise BadRequest(message='Role admin is required')
        items, page_items, count_items = user_repo.get_list(args)
        res = [to_json(item) for item in items]
        return {'items': res, 'page': page_items, 'count': count_items}, 200


@ns.route('/login')
class APIUserLogin(Resource):
    @consumes('application/json')
    @use_args(**{
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'password': {'type': 'string'},
        },
        'required': ['username', 'password']
    })
    def post(self, args):
        username = args.get('username')
        user = user_repo.find_by_username_or_email(username)
        if user:
            if flask_bcrypt.check_password_hash(user.password, args['password']):
                if user.emailVerified:
                    access_token = create_access_token(identity=str(user.id))
                    user = user_repo.change_last_login(user)
                    data = user._data
                    del data['password']
                    data['access_token'] = access_token
                    token_args = {'userId': str(user.id), 'accessToken': access_token}
                    user_access_token = user_access_token_repo.create(token_args)
                    if user_access_token:
                        return {'item': to_json(data), 'message': 'Login successfully'}, 200
                    raise BadRequest(code=400, message='Access token is not created')
                raise BadRequest(code=400, message="Email is not verified")
            raise BadRequest(code=400, message='Invalid username or password')
        raise NotFound(code=404, message="User not found")


@ns.route('/<string:user_id>/logout')
class APIUserLogout(Resource):
    @jwt_required
    @authorized()
    def post(self, current_user, user_id):
        if current_user.roleType == 'User' and (str(current_user.id) != user_id or not current_user.isActive):
            raise BadRequest(message=f'UserId {user_id} is not valid')
        user_access_token_repo.remove_by_user_id(user_id=user_id)
        return {'message': f"Logout {user_id} successfully"}, 204
