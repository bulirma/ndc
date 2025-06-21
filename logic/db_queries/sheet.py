from model.sheet import Sheet


def get_user_by_id(sheet_id: int) -> Sheet:
    return Sheet.query.filter_by(id=sheet_id).first()
