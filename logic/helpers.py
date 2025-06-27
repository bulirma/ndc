import base64
from datetime import datetime
import hashlib
from logic.db_queries import verification_token as vertokdbq
from logic.db_queries import sheet as sheetdbq
from model.sheet import Sheet
import random
import string
import uuid as uuidgen

def hash_email(email: str) -> bytes:
    """
    Hashes the string with SHA-256, which is suitable for hashing emails to prevent duplicate hashes.

    :param email: Email string.
    :return: Email hash.
    """

    hash_str = hashlib.sha256(email.encode('utf-8')).hexdigest()
    return hash_str.encode('utf-8')

def generate_verification_token(length: int = 64) -> str:
    """
    Generates a verification token of a given length (min 32).
    The token starts with random ASCII printable characters and ends with obfuscated UUID for uniqueness.

    :param length: Token length (min 32, default 64).
    :return: Unique token of given length.
    """

    if length < 32:
        raise Exception('token length must be at least 32 characters')

    def sub(char):
        if char == '-':
            return ''
        if char.isalpha():
            return char if random.random() < 0.5 else char.upper()
        return char
        
    # UUID-based part for uniquness
    unique_part = ''.join(map(sub, str(uuidgen.uuid4())))

    if length == 32:
        return unique_part

    # random part
    chars = string.ascii_letters + string.digits + string.punctuation
    random_part = ''.join(random.choice(chars) for _ in range(length - 32))

    return random_part + unique_part

def encode_base64(token: str) -> str:
    """
    Encodes a string in url-safe base64.

    :param token: The input string.
    :return: Encoded input string.
    """

    token_bytes = token.encode('utf-8')
    encoded_bytes = base64.urlsafe_b64encode(token_bytes)
    return encoded_bytes.decode('utf-8')

def decode_base64(encoded_token: str) -> str:
    """
    Decodes an url-safe base64-encoded string.

    :param token: The input string.
    :return: Decoded input string.
    """

    encoded_bytes = encoded_token.encode('utf-8')
    token_bytes = base64.urlsafe_b64decode(encoded_bytes)
    return token_bytes.decode('utf-8')

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

    # TODO: obfuscate the image name
    imn = image_name

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

    return sheetdbq.create_sheet(imn, lc, q, dt, user_id)

