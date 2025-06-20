from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic import helpers
from logic.validation import user as userval
from logic.db_queries import user as userdbq
from logic.db_queries import verification_token as vertokdbq

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
    user = userdbq.get_user_by_email(email)
    if user is None or not user.check_password(password) or user.deactivated_status(True):
        flash('incorrect_credentials_msg', 'danger')
        return render_template('user_access.html', access='login')
    if user.banned_status(True):
        flash('banned_user_msg', 'info')
        return render_template('user_access.html', access='login')
    session['user_id'] = user.id
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
    user = userdbq.get_user_by_email(email)
    if user is not None and user.deactivated_status(False):
        flash('user_already_exists_msg', 'danger')
        return render_template('user_access.html', access='registration', password=password)
    if user is None:
        user = userdbq.create_user(email, password)
    else:
        userdbq.set_user_unverified(user)
    session['user_id'] = user.id
    return redirect(url_for('home.index'))

@user_access_bp.route('/email-verification', defaults={'token': None}, methods=['GET'])
@user_access_bp.route('/email-verification/<token>', methods=['GET'])
def verification(token):
    print('user_id' in session)
    if 'user_id' not in session:
        flash('login_for_verification_msg', 'warning')
        return redirect(url_for('user_access.login'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(False):
        return redirect(url_for('home.index'))
    verification_token = vertokdbq.get_verification_token_by_userid(user.id)
    if verification_token is None:
        if token is None:
            token = helpers.generate_verification_token(128)
            print('generated token:', token)
            vertokdbq.create_verification_token(token, user.id)
            encoded_token = helpers.encode_base64(token)
            return render_template('email_verification.html', token=encoded_token)
        else:
            decoded_token = helpers.decode_base64(token)
            print('obtained token:', decoded_token)
            verification_token = vertokdbq.get_verification_token(decoded_token)
    else:
        if token is None:
            print('obtained token:', verification_token.code)
            encoded_token = helpers.encode_base64(verification_token.code)
            return render_template('email_verification.html', token=encoded_token)
        decoded_token = helpers.decode_base64(token)
    if verification_token is None:
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('user_access.registration'))
    if verification_token.has_expired():
        session.pop('user_id', None)
        vertokdbq.delete_verification_token(verification_token)
        userdbq.delete_user(user)
        flash('expired_verification_token_msg', 'danger')
        return redirect(url_for('home.index'))
    if decoded_token != verification_token.code:
        flash('invalid_verification_token_msg', 'danger')
    else:
        userdbq.set_user_active(user)
        vertokdbq.delete_verification_token(verification_token)
    return redirect(url_for('home.index'))


@user_access_bp.route('/password-recovery')
def password_recovery():
    return render_template('user_access.html')
