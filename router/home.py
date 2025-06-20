from flask import Blueprint, redirect, render_template, session, url_for
from logic.db_queries import user as userdbq

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    if 'user_id' not in session:
        return render_template('index.html')
    user = userdbq.get_user_by_id(session['user_id'])
    return render_template('home.html', user_id=user.id, is_verified=user.unverified_status(False))

@home_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home.index'))
