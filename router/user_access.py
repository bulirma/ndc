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
    if token is not None and not userval.is_token_valid(token):
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('home.index'))
    if 'user_id' not in session:
        flash('login_for_verification_msg', 'warning')
        return redirect(url_for('user_access.login'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(False):
        return redirect(url_for('home.index'))
    verification_token = vertokdbq.get_verification_token_by_userid(user.id)
    if verification_token is None:
        if token is None:
            encoded_token = helpers.generate_user_verification_token(user.id, 128)
            return render_template('email_verification.html', token=encoded_token)
        else:
            decoded_token = helpers.decode_base64(token)
            verification_token = vertokdbq.get_verification_token(decoded_token)
    else:
        if token is None:
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
    flash('email_verified_msg', 'success')
    return redirect(url_for('home.index'))

@user_access_bp.route('/password-recovery', methods=['GET', 'POST'])
def password_recovery_verifaction():
    if request.method == 'GET':
        return render_template('user_access.html', access='password_recovery_email')
    email = request.form['email']
    if not userval.is_email_valid(email):
        flash('invalid_email_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_email')
    user = userdbq.get_user_by_email(email)
    if user is None:
        flash('incorrect_email_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_email')
    verification_token = vertokdbq.get_verification_token_by_userid(user.id)
    if user.unverified_status(True):
        if verification_token is not None:
            vertokdbq.delete_verification_token(verification_token)
        userdbq.delete_user(user)
        flash('unverified_account_deleted_msg', 'warning')
        return redirect(url_for('user_access.login'))
    if verification_token is None:
        encoded_token = helpers.generate_user_verification_token(user.id, 128)
    else:
        encoded_token = helpers.encode_base64(verification_token.code)
    return render_template('password_recovery_verification.html', user_id=user.id, token=encoded_token)

@user_access_bp.route('/password-recovery/<int:user_id>/<token>', methods=['GET', 'POST'])
def password_recovery_prompt(user_id, token):
    if not userval.is_token_valid(token):
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(user_id)
    verification_token = vertokdbq.get_verification_token_by_userid(user_id)
    if user is None or verification_token is None:
        # if token is None it is a suspicious, might be good to notify the user
        flash('user_could_not_be_verified_msg', 'danger')
        return redirect(url_for('user_access.login'))
    decoded_token = helpers.decode_base64(token)
    if verification_token.code != decoded_token:
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('user_access.login'))
    if verification_token.has_expired():
        vertokdbq.delete_verification_token(verification_token)
        flash('expired_verification_token_msg', 'danger')
        return redirect(url_for('user_access.login'))
    if request.method == 'GET':
        return render_template('user_access.html', access='password_recovery_password', user_id=user.id, token=token)
    result = userval.validate_password(request.form)
    if not result.is_password_valid():
        if not result.password_valid_chars:
            flash('invalid_pw_chars_msg', 'danger')
        if not result.password_long_enough:
            flash('pw_too_short_msg', 'danger')
        if not result.password_long_enough:
            flash('pw_too_short_msg', 'danger')
        if not result.password_confirmed:
            flash('pw_not_the_same_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_password', user_id=user.id, token=token)
    userdbq.set_user_password(user, request.form['password'])
    vertokdbq.delete_verification_token(verification_token)
    session['user_id'] = user.id
    flash('new_password_set_msg', 'success')
    return redirect(url_for('home.index'))
