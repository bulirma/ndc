import base64
import re

class PasswordValidatoinResult:
    password_valid_chars = False
    password_long_enough = False
    password_short_enough = False
    password_confirmed = False

    def is_password_valid(self):
        return (self.password_valid_chars and
                self.password_long_enough and
                self.password_short_enough and
                self.password_confirmed)


class UserRegistrationValidationResult(PasswordValidatoinResult):
    email_valid = False
    lang_valid = False

    def is_valid(self):
        return self.email_valid and self.lang_valid and self.is_password_valid()

    def set_password_result(self, password_result: PasswordValidatoinResult):
        self.password_valid_chars = password_result.password_valid_chars
        self.password_long_enough = password_result.password_long_enough
        self.password_short_enough = password_result.password_short_enough
        self.password_confirmed = password_result.password_confirmed

def is_email_valid(email: str) -> bool:
    if len(email) > 256:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_lang_valid(lang: str) -> bool:
    return lang in ('cs', 'en', 'el')

def are_password_chars_valid(password: str) -> bool:
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_-]*$'
    return re.match(pattern, password) is not None

def validate_password(form_data: dict) -> bool:
    result = PasswordValidatoinResult()
    password = form_data['password']
    confirm_password = form_data['confirm-password']

    if are_password_chars_valid(password):
        result.password_valid_chars = True
    if len(password) > 7:
        result.password_long_enough = True
    if len(password) < 65:
        result.password_short_enough = True

    if password == confirm_password:
        result.password_confirmed = True

    return result

def validate_registration_data(form_data: dict) -> UserRegistrationValidationResult:
    result = UserRegistrationValidationResult()
    if is_email_valid(form_data['email']):
        result.email_valid = True
    if is_lang_valid(form_data['lang']):
        result.lang_valid = True
    password_result = validate_password(form_data)
    result.set_password_result(password_result)
    return result

def validate_login_data(form_data: dict) -> bool:
    if len(form_data['email']) == 0:
        return False
    if len(form_data['password']) == 0:
        return False
    return True

def is_token_valid(token: str) -> bool:
    try:
        base64.urlsafe_b64decode(token.encode('utf-8'))
    except:
        return False
    return True
