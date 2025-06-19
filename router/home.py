from flask import Blueprint, redirect, render_template, session, url_for

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    if 'userid' not in session:
        return render_template('index.html')
    user_id = session['userid']
    return render_template('home.html', userid=user_id)

@home_bp.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect(url_for('home.index'))
