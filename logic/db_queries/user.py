from logic.helpers import hash_email
from model import db
from model.user import User

def exists_user(email: str) -> bool:
    users = db.session.query(User)
    return users.filter_by(email_hash=hash_email(email)).first() is not None

def create_user(email: str, password: str) -> User:
    if exists_user(email):
        raise "a user with given email already exists"
    user = User(email, password)
    db.session.add(user)
    db.session.commit()
    return user
