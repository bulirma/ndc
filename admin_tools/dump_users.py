#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import sys

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndc import app
from model import db
from model.user import User

if __name__ == '__main__':
    with app.app_context():
        users = db.session.query(User).all()
    for user in users:
        print(user.get_email())
