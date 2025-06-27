from datetime import datetime
from model import db
from model.sheet import Sheet


def get_sheet_by_id(sheet_id: int) -> Sheet:
    return Sheet.query.filter_by(id=sheet_id).first()

def create_sheet(image_name: str, light_condition: int, quality: int, upload_date: datetime, user_id: int):
    sheet = Sheet(image_name, light_condition, quality, upload_date, user_id)
    db.session.add(sheet)
    db.session.commit()
    return sheet
