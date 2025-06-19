from cryptography.fernet import Fernet
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

__all__ = ['user']

db = SQLAlchemy()
migrate = Migrate()
key = os.getenv('NDC_DB_SECRET_COL_KEY')
if key is None:
    raise Exception('Database secret column key is not provided in ENV')
cipher = Fernet(key.encode('utf-8'))

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
