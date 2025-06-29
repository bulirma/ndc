from datetime import datetime
from model import db
from model.sheet import Sheet


def get_sheet_by_id(sheet_id: int) -> Sheet:
    return Sheet.query.filter_by(id=sheet_id).first()

def get_uploader_sheet_by_id(uploader_id: int, sheet_id: int) -> Sheet:
    return Sheet.query.filter_by(user_id=uploader_id).filter_by(id=sheet_id).first()

def create_sheet(image_name: str, light_condition: int, quality: int, upload_date: datetime, user_id: int):
    sheet = Sheet(image_name, light_condition, quality, upload_date, user_id)
    db.session.add(sheet)
    db.session.commit()
    return sheet

def delete_sheet(sheet: Sheet):
    db.session.delete(sheet)
    db.session.commit()

def get_sheet_count() -> int:
    return Sheet.query.count()

def get_uploader_sheet_batch(user_id: int, offset: int, size: int = 0) -> list:
    if size < 1:
        size = get_sheet_count() - offset
    user_sheets = Sheet.query.filter_by(user_id=user_id)
    return user_sheets.order_by(Sheet.id).offset(offset).limit(size).all()

def sheet_with_uploader_by_image_name(user_id: int, image_name: str) -> bool:
    return Sheet.query.filter_by(user_id=user_id).filter_by(image_name=image_name).first() is not None
