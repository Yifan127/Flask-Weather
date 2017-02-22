import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'weather.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SESSION_TYPE = 'sqlalchemy'
# LOGGER_NAME = 'filelogger'
