from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from celery import Celery
from flask_socketio import SocketIO
import os
import pchess.celeryconfig

import eventlet
eventlet.monkey_patch()

application = Flask(__name__)
Bootstrap(application)

application.config[
    "SQLALCHEMY_DATABASE_URI"
] = os.getenv("DATABASE_URL")
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.app_context().push()

# tell socketio to use eventlet and redis as our msg queue
socketio = SocketIO(application, message_queue=os.getenv("REDIS_URL"), async_mode='eventlet') #'redis://redis:6379'

# init db connection vis sqlalchemy
db = SQLAlchemy(application)
db.init_app(application)

# init migration enginedoc
migrate = Migrate(application, db)

# setup celery for our timed tasks
celery = Celery()
celery.app = application
celery.config_from_object('pchess.celeryconfig')

app = application

from pchess import routes, models


# create the DB on demand, is this a hack or is this a reasonable way
# to do this?
@application.before_first_request
def create_tables():
    db.create_all()


