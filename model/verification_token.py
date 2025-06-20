from . import db
from datetime import datetime

class VerificationToken(db.Model):
    __bind_key__ = 'ndc_users'
    __tablename__ = 'verification_tokens'

    code = db.Column(db.String(128), primary_key=True)
    expiration_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='verification_token')

    def __init__(self, token: str, user_id: int, expiration_date: datetime):
        self.code = token
        self.expiration_date = expiration_date
        self.user_id = user_id

    def has_expired(self) -> bool:
        return datetime.utcnow() > self.expiration_date
