import hashlib

def hash_email(email: str) -> bytes:
    hash_str = hashlib.sha256(email.encode('utf-8')).hexdigest()
    return hash_str.encode('utf-8')
