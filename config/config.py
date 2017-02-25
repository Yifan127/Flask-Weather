import os
from weather import app

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' +\
                          os.path.join(app.root_path, 'weather.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SESSION_TYPE = 'sqlalchemy'
# LOGGER_NAME = 'filelogger'
DEBUG = True
