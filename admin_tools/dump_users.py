#!/usr/bin/env python3

from argparse import ArgumentParser
from dotenv import load_dotenv
import os
import sys

load_dotenv()

parser = ArgumentParser()
parser.add_argument('-t', '--target', type=str, default='users', help='[users|tokens|all]')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from model import db
from model.user import User


def dump_users(include_tokens=False):
    with app.app_context():
        users = db.session.query(User).all()
    max_email_len = len(max(users, key=lambda u: len(u.get_email())).get_email())
    for user in users:
        if user.unverified_status(True):
            status = 'NOT VERIFIED'
        elif user.active_status(True):
            status = 'ACTIVE'
        elif user.deactivated_status(True):
            status = 'DEACTIVATED'
        else:
            status = 'BANNED'
        email = user.get_email()
        padded_email = email + (' ' * (max_email_len - len(email)))
        padded_status = status + (' ' * (12 - len(status)))
        print(f'{padded_email} {padded_status}')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    dump_users()
