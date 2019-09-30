from flask import current_app
from flask_jwt_extended import decode_token

from app import models as m

from .user import user_repo
from bson import ObjectId
from ..utils import _epoch_utc_to_datetime


class UserAccessTokenRepository(object):
    def create(self, args):
        try:
            user_id = args['userId']
            user = user_repo.get_by_id(user_id)
            if user is None:
                return None
            args['userId'] = user.id
            access_token = args['accessToken']
            decoded_token = decode_token(access_token)

            expires = _epoch_utc_to_datetime(decoded_token['exp'])
            created_at = _epoch_utc_to_datetime(decoded_token['iat'])
            args['expireAt'] = expires
            args['CreatedAt'] = created_at
            user_access_token = m.UserAccessToken(**args)
            user_access_token.save()
            return user_access_token
        except Exception as err:
            current_app.logger.error("create user access token error:", err)
            return None

    def get_by_access_token(self, user_id, access_token):
        return m.UserAccessToken.objects(userId=ObjectId(user_id), accessToken=access_token).first()

    def remove_by_user_id(self, user_id):
        return m.UserAccessToken.objects(userId=ObjectId(user_id)).delete()


user_access_token_repo = UserAccessTokenRepository()
