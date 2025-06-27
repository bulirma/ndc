from flask import Blueprint, redirect, render_template, session, url_for
from logic.db_queries import user as userdbq

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    if 'user_id' not in session:
        return render_template('index.html', public=True)
    user = userdbq.get_user_by_id(session['user_id'])
    return render_template('home.html', user_id=user.id, user_unverified=user.unverified_status(True))

@home_bp.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    return render_template('settings.html')

@home_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home.index'))
