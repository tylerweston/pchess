from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from celery import Celery
import os
import pchess.celeryconfig


app = Flask(__name__)
Bootstrap(app)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = os.getenv("DATABASE_URL")
print(f"database uri: f{app.config}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()



# init db connection vis sqlalchemy
db = SQLAlchemy(app)
db.init_app(app)
# db.create_all()
# db.app = app

# init migration engine
migrate = Migrate(app, db)

# setup celery for our timed tasks
celery = Celery()
celery.config_from_object('pchess.celeryconfig')

from pchess import routes, models


# create the DB on demand, is this a hack or is this a reasonable way
# to do this?
@app.before_first_request
def create_tables():
    db.create_all()


