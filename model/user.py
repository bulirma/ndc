from . import cipher, db
import bcrypt
from logic.helpers import hash_email
import os

EMAIL_SALT_LEN = 16
FLAGS_FULL_MASK = 2**16 - 1

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.LargeBinary, unique=True, nullable=False)
    email_hash = db.Column(db.LargeBinary, unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    pref_lang = db.Column(db.String(2), nullable=False)
    flags = db.Column(db.SmallInteger, nullable=False)

    verification_token = db.relationship('VerificationToken', back_populates='user', uselist=False)
    sheets = db.relationship('Sheet', backref='uploader', lazy=True)

    def __init__(self, email: str, password: str):
        self.set_email(email)
        self.set_password(password)
        self.pref_lang = 'en'
        self.flags = 0

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

    def unverified_status(self, value: bool) -> bool:
        status = self.flags & 3
        return (status == 0) == value

    def active_status(self, value: bool) -> bool:
        status = self.flags & 3
        return (status == 1) == value

    def deactivated_status(self, value: bool) -> bool:
        status = self.flags & 3
        return (status == 2) == value

    def banned_status(self, value: bool) -> bool:
        status = self.flags & 3
        return (status == 3) == value

    def set_unverified(self):
        flags = self.flags & (FLAGS_FULL_MASK - 3)
        self.flags = flags

    def set_active(self):
        flags = self.flags & (FLAGS_FULL_MASK - 3)
        self.flags = flags + 1
