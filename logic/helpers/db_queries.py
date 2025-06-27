from datetime import datetime
from logic.db_queries import verification_token as vertokdbq
from logic.db_queries import sheet as sheetdbq
import math
from .cryptography import generate_verification_token, encode_base64
from model.sheet import Sheet
import os


def generate_user_verification_token(user_id: int, length: int = 64) -> str:
    """
    Helper function to generate verification token for given user.

    :param user_id: User ID.
    :param length: Token length.
    :return: Verification token.
    """

    token = generate_verification_token(128)
    vertokdbq.create_verification_token(token, user_id)
    return encode_base64(token)

def create_sheet_record(image_name: str, light_condition: str, quality: str, user_id: int) -> Sheet:
    """
    Helper function to create a sheet record with form values.

    :param image_name: Image name.
    :param light_condition: Textual representation of light condition.
    :param quality: Textual representation of quality.
    :param user_id: Uploader user ID.
    :return: Sheet model object.
    """

    if light_condition == 'dark':
        lc = 0
    elif light_condition == 'dimmed':
        lc = 1
    elif light_condition == 'light':
        lc = 2
    elif light_condition == 'flashlight':
        lc = 3
    else:
        raise Exception('unknown level of sheet light condition')

    if quality == 'poor':
        q = 0
    elif quality == 'satisfactory':
        q = 1
    elif quality == 'good':
        q = 2
    else:
        raise Exception('unknown level of sheet quality')

    dt = datetime.utcnow()

    start = datetime(dt.year, dt.month, dt.day)
    day_elapsed_time = dt - start

    _, extension = os.path.splitext(image_name)
    name = 'SHEET_' + light_condition[: 2].upper() + quality[: 2].upper() + \
        '_' + str(day_elapsed_time.total_seconds()).zfill(5) + extension

    return sheetdbq.create_sheet(name, lc, q, dt, user_id)

def get_pages(page_record_count: int) -> int:
    total = sheetdbq.get_sheet_count()
    return math.ceil(total / page_record_count)

def get_page_records(user_id: int, page: int, count: int) -> list:
    return sheetdbq.get_uploader_sheet_batch(user_id, page * count, count)
