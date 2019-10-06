from datetime import datetime

import jwt
from bson import ObjectId
from flask import current_app

from app import models as m
from app.extensions import flask_bcrypt
from app.helper import Helper


class UserRepository(object):

    def get_list(self, args):
        sortable_fields = ['createdAt', 'createdBy', 'updatedAt', 'updatedBy', 'isActive',
                           'company', 'email', 'address', 'billingType', 'roleType', 'username', 'lastSignin']
        page = Helper.get_page_from_args(args)
        size = Helper.get_size_from_args(args)
        optional = args.get('optional')
        sorts = Helper.get_sort_from_args(args, sortable_fields)
        fields = Helper.get_fields_from_args(args)
        if sorts is not None:
            args = []
            for sort in sorts:
                column = getattr(m.User, sort[0])
                sort_method = '-' if sort[1] == 'desc' else ''
                args.append(sort_method + column.name)
            if optional is not None and optional == 'all':
                items = m.User.objects.order_by(*args)
                page_items = None
                count_items = len(items)
            else:
                users = m.User.objects.order_by(*args).paginate(page=page, per_page=size)
                items, page_items, count_items = users.items, users.page, users.total
        res = []
        for item in items:
            data = {k: item._data[k] for k in item._data if (fields is None or k in fields) and k != 'password'}
            res.append(data)

        return res, page_items, count_items

    def verify_user(self, user):
        user.update(emailVerified=True)
        user.reload()
        return user

    def generate_reset_password_token(self, user):
        now = datetime.utcnow()
        payload = {
            'email': user.email,
            'user': str(user.id),
            'iat': now,
            'exp': now + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'),
        }
        token = jwt.encode(payload, current_app.config.get('SECRET_KEY'), algorithm='HS256').decode('utf-8')
        return token

    def generate_registration_token(self, user):
        payload = {
            'user': str(user.id),
            'email': user.email,
            'iat': user.createdAt,
            'exp': user.createdAt + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'),
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        return token

    def get_user_from_token_reset_password(self, token):
        secret_key = current_app.config.get('SECRET_KEY')
        try:
            claims = jwt.decode(token, key=secret_key, algorithms=['HS256'])
        except jwt.DecodeError as err:
            current_app.logger.error(err)
            return None, 'Could not get information'
        except jwt.ExpiredSignatureError as err:
            current_app.logger.error(err)
            return None, 'Signature expired'
        except jwt.InvalidTokenError as err:
            current_app.logger.error(err)
            return None, 'Invalid token'
        user_id = claims.get('user')
        email = claims.get('email')
        created_at = claims.get('iat')
        expired_at = claims.get('exp')
        if user_id is None or email is None or created_at is None or expired_at is None:
            return None, 'Token is not valid'
        user = m.User.objects(id=ObjectId(user_id)).first()
        if user is None or user.email != email:
            return None, 'Token is not valid'
        if not user.emailVerified:
            return None, 'Email is not verified'
        return user, None

    def get_user_from_token_registration(self, token):
        secret_key = current_app.config.get('SECRET_KEY')
        try:
            claims = jwt.decode(token, key=secret_key, algorithms=['HS256'])
        except jwt.DecodeError as err:
            current_app.logger.error(err)
            return None, 'Could not get information'
        except jwt.ExpiredSignatureError as err:
            current_app.logger.error(err)
            return None, 'Signature expired'
        except jwt.InvalidTokenError as err:
            current_app.logger.error(err)
            return None, 'Invalid token'

        user_id = claims.get('user')
        email = claims.get('email')
        created_at = claims.get('iat')
        expired_at = claims.get('exp')
        if user_id is None or email is None or created_at is None or expired_at is None:
            return None, 'Token is not valid'
        # TODO: SangLX - get information from token
        user = m.User.objects(id=ObjectId(user_id)).first()
        if user is None or user.email != email:
            return None, 'Token is not valid'
        if user.emailVerified:
            return None, 'Email is verified'
        return user, None

    def get_by_id(self, user_id):
        return m.User.objects(id=ObjectId(user_id)).first()

    def insert_one(self, data):
        if 'email' in data and m.User.objects(email=data['email']).first() is not None:
            return None, 'Email existing'
        if 'username' in data and m.User.objects(username=data['username']).first() is not None:
            return None, 'Username existing'
        user = m.User(**data)
        user.save()
        return user, None

    def find_by_username_or_email(self, username):
        user = m.User.objects(username=username).first()
        if user is None:
            user = m.User.objects(email=username).first()
        return user

    def change_last_login(self, user):
        last_sign_in = datetime.utcnow()
        user.update(lastSignin=last_sign_in)
        user.reload()
        return user

    def update_user(self, user, current_user, args):
        args['updatedAt'] = datetime.utcnow()
        if current_user is not None:
            args['updatedBy'] = current_user.username
        if 'password' in args:
            args['password'] = flask_bcrypt.generate_password_hash(args['password']).decode('utf-8')
        try:
            user.update(**args)
            user.reload()
            return user
        except Exception as e:
            current_app.logger.error('exception on user update:', e)
            user.reload()
            return user

    def get_by_email(self, email):
        return m.User.objects(email=email).first()


user_repo = UserRepository()
