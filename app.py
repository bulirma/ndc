from dotenv import load_dotenv
from flask import Flask, request, session
from flask_babel import Babel
import logging
from model import init_db
from router import home_bp, user_access_bp, sheet_collection_bp
from router import set_sheet_upload_directory
import os



load_dotenv()

app = Flask(__name__)

app.secret_key = os.urandom(64)

logging.basicConfig(level=logging.DEBUG)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ndc.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'
app.config['UPLOAD_SHEETS_DIRECTORY'] = './instance/sheets'
app.config['LANGUAGES'] = ['cs', 'en', 'gr']

def get_locale():
    if 'lang' in session:
        return session.get('lang', 'en')
    return request.accept_languages.best_match(app.config['LANGUAGES'])

if not os.path.exists(app.config['UPLOAD_SHEETS_DIRECTORY']):
    os.mkdir(app.config['UPLOAD_SHEETS_DIRECTORY'])

app.register_blueprint(home_bp)
app.register_blueprint(user_access_bp)
app.register_blueprint(sheet_collection_bp)

babel = Babel()
babel.init_app(app, locale_selector=get_locale)

init_db(app)
set_sheet_upload_directory(app.config['UPLOAD_SHEETS_DIRECTORY'])
