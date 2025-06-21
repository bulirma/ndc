#!/usr/bin/env python3

from argparse import ArgumentParser
from dotenv import load_dotenv
import math
import re
import os
import sys

load_dotenv()

DEFAULT_BATCH_SIZE = 100
MIN_BATCH_SIZE = 32

parser = ArgumentParser()
parser.add_argument('-i', '--token_info', action='store_true', help='include tokens')
parser.add_argument('-o', '--token', type=str, default='all',
                    help='users having token (all|yes|no)')
parser.add_argument('-s', '--status', type=str, default='all',
                    help='users only with token status (all|valid|expired) (only with [-o|--token]=yes')
parser.add_argument('-t', '--target', type=str, default='all',
                    help='user status (all|unverified|active|deactivated|banned)')
parser.add_argument('-r', '--untarget', action='store_true',
                    help='users with other status than specified (only with [-t|--target] option, except all')
parser.add_argument('-m', '--match', type=str, default=None, help='regex for matching user email')
parser.add_argument('-v', '--unmatch', action='store_true',
                    help='users with email not matching the pattern (only with [-m|--match] option)')
parser.add_argument('-b', '--batch', type=int, default=DEFAULT_BATCH_SIZE,
                    help=f'batch size of processed users ({MIN_BATCH_SIZE} minumum)')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from model.user import User
from model.verification_token import VerificationToken

def validate_args(args):
    if args.batch < MIN_BATCH_SIZE:
        return False
    if args.token not in ('all', 'yes', 'no'):
        return False
    if args.status not in ('all', 'valid', 'expired'):
        return False
    if args.target not in ('all', 'unverified', 'active', 'deactivated', 'banned'):
        return False
    return True

def get_users(status: str, reverse_status: bool, offset: int, limit: int) -> list:
    with app.app_context():
        users_query = User.query.order_by(User.id)
        if status == 'all':
            users_by_status_query = users_query
        elif status == 'unverified':
            users_by_status_query = users_query.filter((User.flags.op('&')(3) == 0) != reverse_status)
        elif status == 'active':
            users_by_status_query = users_query.filter((User.flags.op('&')(3) == 1) != reverse_status)
        elif status == 'deactivated':
            users_by_status_query = users_query.filter((User.flags.op('&')(3) == 2) != reverse_status)
        else:
            users_by_status_query = users_query.filter((User.flags.op('&')(3) == 3) != reverse_status)
        return users_by_status_query.offset(offset).limit(limit).all()

def get_user_text_status(user: User) -> str:
    if user.unverified_status(True):
        return 'NOT VERIFIED'
    if user.active_status(True):
        return 'ACTIVE'
    if user.deactivated_status(True):
        return 'DEACTIVATED'
    return 'BANNED'

def invalid_print_token_constraints(token: VerificationToken, having_token: str, token_status: str) -> bool:
    if having_token == 'yes':
        if token is None:
            return True
        if token.has_expired() and token_status == 'valid':
            return True
        if not token.has_expired() and token_status == 'expired':
            return True
    if having_token == 'no' and token is not None:
        return True
    return False

def get_num_len(num: int):
    return math.ceil(math.log10(num))

def dump_users(args):
    having_token = args.token
    token_info = args.token_info
    token_status = args.status
    status = args.target
    reverse_status = args.untarget
    email_pattern = args.match
    reverse_match = args.unmatch
    batch_size = args.batch
    
    with app.app_context():
        count = User.query.count()
    offset = 0
    batch_size = batch_size if batch_size > 0 else count
    while offset < count:
        if offset + batch_size > count:
            batch_size = count - offset
        users = get_users(status, reverse_status, offset, batch_size)
        max_email_len = len(max(users, key=lambda u: len(u.get_email())).get_email())
        max_id_len = get_num_len(users[-1].id)
        if max_id_len == 0:
            max_id_len = 1
        for user in users:
            # check email constraints
            if email_pattern is not None:
                if (re.search(email_pattern, user.get_email()) is None) != reverse_match:
                    continue

            # prepare user data
            text_status = get_user_text_status(user)
            email = user.get_email()
            padded_id = str(user.id) + (' ' * (max_id_len - get_num_len(user.id)))
            padded_email = email + (' ' * (max_email_len - len(email)))
            padded_status = text_status + (' ' * (12 - len(text_status)))
            with app.app_context():
                token = VerificationToken.query.filter_by(user_id=user.id).first()

            # check token constraints
            if invalid_print_token_constraints(token, having_token, token_status):
                continue

            # prepare token data
            if token_info and token is not None:
                token_code = token.code
                expiration_date = token.expiration_date

            # print
            if token_info and token is not None:
                print(f'{padded_id} \t{padded_email} \t{padded_status} \t{expiration_date} \t{token_code}')
            else:
                print(f'{padded_id} \t{padded_email} \t{padded_status}')

        offset += batch_size


if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    if validate_args(args):
        dump_users(args)
    else:
        print('incorrect arguments, check help', file=sys.stderr)
        os.exit(1)
