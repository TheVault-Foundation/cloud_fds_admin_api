from flask_jwt_extended import (create_access_token, get_jwt_identity,  # noqa
                                jwt_required)
from flask_restplus import Namespace, Resource
from flask import jsonify

from app.errors.exceptions import BadRequest
from app.extensions import flask_bcrypt, jwt_manager
from app.repositories.transaction import tran_repo
from app.repositories.user import user_repo

from ..utils import consumes, to_json, use_args

ns = Namespace(name="users", description="Users related operation")


@jwt_manager.invalid_token_loader
def invalid_token_callback(callback):
    return jsonify({'error': {'message': 'Invalid token', 'code': 401}}), 401


@jwt_manager.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'error': {'message': 'Missing authorization header', 'code': 401}}), 401


@jwt_manager.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({'error': {'message': 'The {} token has expired'.format(token_type), 'code': 401}}), 401


@ns.route('/<string:user_id>/transactions')
class APITransactionList(Resource):
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
    @jwt_required
    def get(self, args, user_id):
        items, page_items, count_items = tran_repo.get_transaction_list(args)
        res = [to_json(item) for item in items]
        return {'items': res, 'page': page_items, 'count': count_items}, 200


@ns.route('')
class APIUserRegister(Resource):
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
                'pattern': '^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$'
            }
        },
        'required': ['email', 'password']
    })
    def post(self, args):
        ''' register user endpoint '''
        role_type = args.get('roleType', 'User')
        if role_type not in ['Admin', 'User']:
            raise BadRequest(message='Role type must be Admin or User')
        args['createdBy'] = args.get('createdBy', 'Admin')
        args['roleType'] = role_type
        if 'username' not in args and 'email' not in args:
            raise BadRequest(code=400, message='username or email must be required')
        args['password'] = flask_bcrypt.generate_password_hash(args['password'])
        user, message = user_repo.insert_one(args)
        if user is None:
            raise BadRequest(code=400, message=message)
        return {'item': to_json(user._data), 'message': 'Signup user is successful'}, 201


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
        if user.roleType == 'User':
            raise BadRequest(code=400, message='RoleType is not valid')
        if user and flask_bcrypt.check_password_hash(user.password, args['password']):
            data = user._data
            del data['password']
            access_token = create_access_token(identity=str(user.id))
            data['access_token'] = access_token
            return {'item': to_json(data), 'message': 'Login successfully'}, 200
        else:
            raise BadRequest(code=400, message='Invalid username or password')
