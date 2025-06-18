#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndc import app
from model import db

if __name__ == '__main__':
    with app.app_context():
        db.create_all(bind_key='ndc-users')
        db.create_all(bind_key='ndc-sheets')
