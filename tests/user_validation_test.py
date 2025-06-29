import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.validation import user as userval

def test_email_valid():
    emails = [
        '_@9.odd',
        'MrSecret@public.place',
        'this-is@Also-completely.valid'
    ]
    for email in emails:
        assert userval.is_email_valid(email)

def test_email_invalid():
    emails = [
        '@.',
        'me@here',
        'this-is@not_.tho',
        ('too_long' * 35) + '@email.is.not.valid'
    ]
    for email in emails:
        assert not userval.is_email_valid(email)

def test_password_valid_chars():
    passwords = [
        '1234567890',
        's0m3G00dch4r$_-',
        'SHORT',
        '@llThoseToo!#$%^&*()'
    ]
    for password in passwords:
        assert userval.are_password_chars_valid(password)

def test_password_invalid_chars():
    passwords = [
        'tilde~',
        'slaches/\\',
        'question?',
        '+:.'
    ]
    for password in passwords:
        assert not userval.are_password_chars_valid(password)

def test_lang_valid():
    langs = ['cs', 'en', 'el']
    for lang in langs:
        assert userval.is_lang_valid(lang)

def test_lang_invalid():
    langs = ['de', 'es']
    for lang in langs:
        assert not userval.is_lang_valid(lang)

def test_registration_valid():
    form_data = {
        'email': 'some-email123@mail.example.com',
        'password': 'd1ff1cULTp@$$w0rd',
        'confirm-password': 'd1ff1cULTp@$$w0rd',
        'lang': 'cs'
    }
    result = userval.validate_registration_data(form_data)
    assert result.is_valid()

def test_registration_invalid_password_1():
    form_data = {
        'email': 'good@mail.example.com',
        'password': 'short',
        'confirm-password': 'and_n0t-THEs4m3',
        'lang': 'en'
    }
    result = userval.validate_registration_data(form_data)
    assert result.email_valid
    assert result.lang_valid
    assert result.password_valid_chars
    assert not result.password_long_enough
    assert result.password_short_enough
    assert not result.password_confirmed

def test_registration_invalid_password_2():
    form_data = {
        'email': 'good@mail.example.com',
        'password': '~t00Lo_ng' * 9,
        'confirm-password': '~t00Lo_ng' * 9,
        'lang': 'es'
    }
    result = userval.validate_registration_data(form_data)
    assert result.email_valid
    assert not result.lang_valid
    assert not result.password_valid_chars
    assert result.password_long_enough
    assert not result.password_short_enough
    assert result.password_confirmed

def test_login_valid():
    form_data = {
        'email': 'good@mail.example.com',
        'password': 'g00dp4$$WORD_r3a1ly',
    }
    assert userval.validate_login_data(form_data)

def test_login_invalid():
    form_data = {
        'email': '',
        'password': '',
    }
    assert not userval.validate_login_data(form_data)
