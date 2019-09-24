import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something-very-secret'
    MONGODB_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGODB_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGODB_HOST = os.environ.get('MONGO_HOST') or 'localhost'
    MONGODB_PORT = int(os.environ.get('MONGO_PORT')) or 27017
    MONGODB_DB = os.environ.get('MONGO_DATABASE') or 'cloudFDS'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)


class TestingConfig(Config):
    TESTING = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


configs = {
    'develop': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
