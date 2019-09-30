from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from flask_mail import Mail


ma = Marshmallow()
flask_bcrypt = Bcrypt()
jwt_manager = JWTManager()
db = MongoEngine()
cors = CORS()
mail = Mail()


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
