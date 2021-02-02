from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from celery import Celery
from flask_socketio import SocketIO
import os
import pchess.celeryconfig


app = Flask(__name__)
Bootstrap(app)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = os.getenv("DATABASE_URL")
print(f"DB URL: " + os.getenv("DATABASE_URL"))
print(f"database uri: f{app.config}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()

# hmm, using the message queue like this seems to cause problems else where
# but without using it, how do we send socketio messages from celery workers?
# hmmmm
socketio = SocketIO(app, message_queue='redis://redis:6379', async_mode='threading')
#socketio = SocketIO(app)


# init db connection vis sqlalchemy
db = SQLAlchemy(app)
db.init_app(app)
# db.create_all()
# db.app = app

# init migration enginedoc
migrate = Migrate(app, db)

# CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
# CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

# setup celery for our timed tasks
celery = Celery()
celery.app = app
celery.config_from_object('pchess.celeryconfig')

# # from
# # https://github.com/kwiersma/flask-celery-sqlalchemy/blob/master/app/celeryapp/__init__.py
#
# TaskBase = celery.Task
#
# class ContextTask(TaskBase):
#     abstract = True
#
#     def __call__(self, *args, **kwargs):
#         if not celery.conf.CELERY_ALWAYS_EAGER:
#             with app.app_context():
#                 # Flask-SQLAlchemy doesn't appear to create a SQLA session that is thread safe for a
#                 # Celery worker to use. To get around that we can just go ahead and create our own
#                 # engine and session specific to this Celery task run.
#                 #
#                 # Connection Pools with multiprocessing:
#                 # https://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
#                 #
#                 # FMI: https://stackoverflow.com/a/51773204/920389
#                 # db.session.remove()
#                 # db.session.close_all()
#                 # db.engine.dispose()
#                 #
#                 # engine = create_engine(_app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
#                 # db_sess = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
#                 # db.session = db_sess
#
#                 return TaskBase.__call__(self, *args, **kwargs)
#         else:
#             # special pytest setup
#             # db.session = models.db.session = db_session
#             db.session = None
#             return TaskBase.__call__(self, *args, **kwargs)
#
#     def after_return(self, status, retval, task_id, args, kwargs, einfo):
#         """
#         After each Celery task, teardown our db session.
#         FMI: https://gist.github.com/twolfson/a1b329e9353f9b575131
#         Flask-SQLAlchemy uses create_scoped_session at startup which avoids any setup on a
#         per-request basis. This means Celery can piggyback off of this initialization.
#         """
#         if app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']:
#             if not isinstance(retval, Exception):
#                 db.session.commit()
#         # If we aren't in an eager request (i.e. Flask will perform teardown), then teardown
#         if not celery.conf.CELERY_ALWAYS_EAGER:
#             db.session.remove()
#
#
# celery.Task = ContextTask
from pchess import routes, models


# create the DB on demand, is this a hack or is this a reasonable way
# to do this?
@app.before_first_request
def create_tables():
    db.create_all()


