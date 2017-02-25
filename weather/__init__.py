import os
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session, SqlAlchemySessionInterface
# from logconfig import LOGGING


# Define the WSGI application object
app = Flask(__name__)
# Configuration
app.config.from_object('config.config')
app.secret_key = 'ae25be573f1b6e19a066fe920685137cb5ea4f76e5924173'

# Define the database object
db = SQLAlchemy(app)

# Session
Session(app)
app.session_interface = SqlAlchemySessionInterface(app, db, 'session', '')

# Log
'''
logger = app.logger
logging.config.dictConfig(LOGGING)
'''
logfile = os.path.join(app.root_path, 'weather.log')
handler = RotatingFileHandler(logfile, maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
                               '[in %(module)s - %(funcName)s:%(lineno)d]'))
app.logger.addHandler(handler)


from .weather.views import weather
from .api_v1.weather import api_bp
# Register blueprint(s)
app.register_blueprint(weather)
app.register_blueprint(api_bp)

from .weather.models import Description
# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
Description.load_description()
