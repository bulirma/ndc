from flask import Blueprint, render_template

user_access_bp = Blueprint('user_access', __name__)

@user_access_bp.route('/login')
def login():
    return render_template('user_access.html')
