from flask import Flask, request
from flask_babel import Babel
from model import init_db
from router import index_bp, user_access_bp

app = Flask(__name__)

def get_locale():
    return request.accept_languages.best_match(['en'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ndc-default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'ndc-users': 'sqlite:///ndc-users.db',
    'ndc-sheets': 'sqlite:///ndc-sheets.db'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'

app.register_blueprint(index_bp)
app.register_blueprint(user_access_bp)

babel = Babel()
babel.init_app(app, locale_selector=get_locale)

init_db(app)
