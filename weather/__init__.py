import json
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
app.config.from_object('config')
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
handler = RotatingFileHandler('weather.log', maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
                               '[in %(module)s - %(funcName)s:%(lineno)d]'))
app.logger.addHandler(handler)


from weather.views import weather
from weather.models import Description
# Register blueprint(s)
app.register_blueprint(weather)


# load weather description
def load_description():
    with open('description.json', encoding='utf-8') as file:
        text = file.readlines()
        for line in text:
            data = json.loads(line)
            record = Description(data['desc_id'], data['group'],
                                 data['description'])
            db.session.add(record)
            db.session.commit()


# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
load_description()
