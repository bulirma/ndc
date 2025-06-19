from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic.validation import user as userval
from logic.db_queries import user as userdbq

user_access_bp = Blueprint('user_access', __name__)

@user_access_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user_access.html', access='login')
    if not userval.validate_login_data(request.form):
        flash('missing_input_msg', 'danger')
        return render_template('user_access.html', access='login')
    email = request.form['email']
    password = request.form['password']
    user = userdbq.get_user(email)
    if user is None or not user.check_password(password):
        flash('incorrect_credentials_msg', 'danger')
        return render_template('user_access.html', access='login')
    session['userid'] = user.id
    return redirect(url_for('home.index'))

@user_access_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('user_access.html', access='registration')
    result = userval.validate_registration_data(request.form)
    if not result.is_valid():
        email = None
        if result.email_valid:
            email = request.form['email']
        else:
            flash('invalid_email_msg', 'danger')
        if not result.is_password_valid():
            if not result.password_valid_chars:
                flash('invalid_pw_chars_msg', 'danger')
            if not result.password_long_enough:
                flash('pw_too_short_msg', 'danger')
            if not result.password_long_enough:
                flash('pw_too_short_msg', 'danger')
            if not result.password_confirmed:
                flash('pw_not_the_same_msg', 'danger')
        return render_template('user_access.html', access='registration', email=email)
    email = request.form['email']
    password = request.form['password']
    if userdbq.exists_user(email):
        flash('user_already_exists_msg', 'danger')
        return render_template('user_access.html', access='registration', password=password)
    user = userdbq.create_user(email, password)
    session['userid'] = user.id
    return redirect(url_for('home.index'))

@user_access_bp.route('/password-recovery')
def password_recovery():
    return render_template('user_access.html')
