import base64
import hashlib
import random
import string
import uuid as uuidgen

def hash_email(email: str) -> bytes:
    hash_str = hashlib.sha256(email.encode('utf-8')).hexdigest()
    return hash_str.encode('utf-8')

def generate_verification_token(length: int = 64) -> str:
    if length < 32:
        raise "token length must be at least 32 characters"

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
    token_bytes = token.encode('utf-8')
    encoded_bytes = base64.b64encode(token_bytes)
    return encoded_bytes.decode('utf-8')

def decode_base64(encoded_token: str) -> str:
    encoded_bytes = encoded_token.encode('utf-8')
    token_bytes = base64.b64decode(encoded_bytes)
    return token_bytes.decode('utf-8')
