from . import db
from datetime import datetime

class Sheet(db.Model):
    __tablename__ = 'sheets'

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(64), unique=True, nullable=False)
    light_condition = db.Column(db.SmallInteger, nullable=False)
    quality = db.Column(db.SmallInteger, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self,
                 image_name: str,
                 light_condition: int,
                 quality: int,
                 upload_date: datetime,
                 user_id: int):
        self.image_name = image_name
        self.light_condition = light_condition
        self.quality = quality
        self.upload_date = upload_date
        self.user_id = user_id
