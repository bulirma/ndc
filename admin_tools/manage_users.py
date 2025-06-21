#!/usr/bin/env python3

from argparse import ArgumentParser
from dotenv import load_dotenv
import os
import sys

load_dotenv()

parser = ArgumentParser()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from model import db
from model.user import User
from model.verification_token import VerificationToken


def validate_args(args):
    return True

def manage_users(args):
    user_data = sys.stdin.read()
    users = [line.split() for line in user_data.splitlines()]
    for user in users:
        user_id = int(user[0])
        with app.app_context():
            user = User.query.filter_by(id=user_id).first()
            token = VerificationToken.query.filter_by(user_id=user_id).first()
            if token is not None:
                db.session.delete(token)
            db.session.delete(user)
            db.session.commit()
    

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    if validate_args(args):
        manage_users(args)
    else:
        print('incorrect arguments, check help', file=sys.stderr)
        os.exit(1)
