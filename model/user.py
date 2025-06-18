from . import db, cipher
from logic.helpers import hash_email
import bcrypt
import os

EMAIL_SALT_LEN = 16

class User(db.Model):
    __bind_key__ = 'ndc-users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.LargeBinary, unique=True, nullable=False)
    email_hash = db.Column(db.LargeBinary, unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    pref_lang = db.Column(db.String(2), nullable=False)
    flags = db.Column(db.SmallInteger, nullable=False)

    def __init__(self, email: str, password: str):
        self.set_email(email)
        self.set_password(password)
        self.pref_lang = 'en'
        self.flags = 1

    def set_email(self, email: str):
        salt = os.urandom(EMAIL_SALT_LEN)
        email_value = email.encode('utf-8') + salt
        self.email = cipher.encrypt(email_value)
        self.email_hash = hash_email(email)

    def get_email(self) -> str:
        email_value = cipher.decrypt(self.email)
        email = email_value[: -EMAIL_SALT_LEN].decode('utf-8')
        return email

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def set_pref_lang(self, pref_lang: str):
        self.pref_lang = pref_lang

    def get_pref_lang(self) -> str:
        return self.pref_lang
