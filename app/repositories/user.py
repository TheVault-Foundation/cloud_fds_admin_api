from datetime import datetime

import jwt
from bson import ObjectId
from flask import current_app

from app import models as m
from app.errors.exceptions import BadRequest
from app.extensions import flask_bcrypt


class UserRepository(object):

    def verify_user(self, user):
        user.update(emailVerified=True)
        user.reload()
        return user

    def generate_registration_token(self, user):
        payload = {
            'user': str(user.id),
            'email': user.email,
            'iat': user.createdAt,
            'exp': user.createdAt + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES'),
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        return token

    def get_user_from_token(self, token):
        secret_key = current_app.config.get('SECRET_KEY')
        try:
            claims = jwt.decode(token, key=secret_key, algorithms=['HS256'])
        except jwt.DecodeError as err:
            current_app.logger.error(err)
            raise BadRequest(message='Could not get information')
        except jwt.ExpiredSignatureError as err:
            current_app.logger.error(err)
            raise BadRequest(message='Signature expired')
        except jwt.InvalidTokenError as err:
            current_app.logger.error(err)
            raise BadRequest(message='Invalid token')

        user_id = claims.get('user')
        email = claims.get('email')
        created_at = claims.get('iat')
        expired_at = claims.get('exp')
        if user_id is None or email is None or created_at is None or expired_at is None:
            raise BadRequest(message='Token is not valid')
        # TODO: SangLX - get information from token
        user = m.User.objects(id=ObjectId(user_id)).first()
        if user is None or user.email != email:
            raise BadRequest(message='Token is not valid')
        if user.emailVerified:
            raise BadRequest(message='Email is verified')
        return user

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


user_repo = UserRepository()
