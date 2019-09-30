import os

from dotenv import load_dotenv

load_dotenv(override=True)

from app import create_app  # noqa
from app.config import configs as config  # noqa

config_name = os.environ.get('FLASK_CONFIG') or 'develop'
config_cls = config[config_name]
application = app = create_app(config_cls)
