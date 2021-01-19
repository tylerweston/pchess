from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import pchess.celeryconfig


app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:password@localhost:5432/pchess"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



# init db connection vis sqlalchemy
db = SQLAlchemy(app)

# init migration engine
migrate = Migrate(app, db)

# setup celery for our timed tasks
#celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery = Celery()
celery.config_from_object('pchess.celeryconfig')

from pchess import routes, models

# def create_app(test_config=None):
#     # basic flask app setup
#     app = Flask(__name__)
#     app.config[
#         "SQLALCHEMY_DATABASE_URI"
#     ] = "postgresql://postgres:password@localhost:5432/pchess"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#
#     return app