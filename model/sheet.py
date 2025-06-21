from . import db

class Sheet(db.Model):
    __tablename__ = 'sheets'

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(64), unique=True, nullable=False)
    light_condition = db.Column(db.SmallInteger, nullable=False)
    quality = db.Column(db.SmallInteger, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
