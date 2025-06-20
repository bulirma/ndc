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
from model.verification_token import VerificationToken


def dump_users(include_tokens=False):
    tokens = None
    with app.app_context():
        users = User.query.order_by(User.id).all()
        if include_tokens:
            tokens = VerificationToken.query.order_by(VerificationToken.user_id).all()
    max_email_len = len(max(users, key=lambda u: len(u.get_email())).get_email())
    token_idx = 0
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
        token = None
        if tokens is not None and len(tokens) > 0 and user.id == tokens[token_idx].user_id:
            token = tokens[token_idx].code
            token_idx += 1
        if token is None:
            print(f'{padded_email} {padded_status}')
        else:
            print(f'{padded_email} {padded_status} token: {token}')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    if args.target == 'all':
        dump_users(True)
    elif args.target == 'users':
        dump_users()
    else:
        pass
