from datetime import datetime, timedelta
from model import db
from model.verification_token import VerificationToken


def get_verification_token(token: str) -> VerificationToken:
    return VerificationToken.query.filter_by(code=token).first()

def get_verification_token_by_userid(user_id: int) -> VerificationToken:
    return VerificationToken.query.filter_by(user_id=user_id).first()

def create_verification_token(token: str, user_id: int, expiration_date: datetime = None) -> VerificationToken:
    if expiration_date is None:
        expiration_date = datetime.utcnow() + timedelta(days=1)
    verification_token = VerificationToken(token, user_id, expiration_date)
    db.session.add(verification_token)
    db.session.commit()
    return verification_token

def delete_verification_token(verification_token: VerificationToken):
    db.session.delete(verification_token)
    db.session.commit()
