from logic.helpers import hash_email
from model import db
from model.user import User


def get_user_by_id(user_id: int) -> User:
    return User.query.filter_by(id=user_id).first()

def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email_hash=hash_email(email)).first()

def create_user(email: str, password: str, pref_lang: str) -> User:
    user = User(email, password, pref_lang)
    db.session.add(user)
    db.session.commit()
    return user

def delete_user(user: User):
    db.session.delete(user)
    db.session.commit()

def set_user_unverified(user: User):
    user.set_unverified()
    db.session.commit()

def set_user_active(user: User):
    user.set_active()
    db.session.commit()

def set_user_password(user: User, password: str):
    user.set_password(password)
    db.session.commit()
