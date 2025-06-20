from dotenv import load_dotenv
from flask import Flask, request
from flask_babel import Babel
import logging
from model import init_db
from router import home_bp, user_access_bp
import os


def get_locale():
    return request.accept_languages.best_match(['en'])

load_dotenv()

app = Flask(__name__)

app.secret_key = os.urandom(64)

logging.basicConfig(level=logging.DEBUG)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ndc-default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'ndc_users': 'sqlite:///ndc-users.db',
    'ndc_sheets': 'sqlite:///ndc-sheets.db'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'

app.register_blueprint(home_bp)
app.register_blueprint(user_access_bp)

babel = Babel()
babel.init_app(app, locale_selector=get_locale)

init_db(app)
