from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic.helpers.cryptography import decode_base64, encode_base64
from logic.helpers.db_queries import generate_user_verification_token
from logic.validation import user as userval
from logic.db_queries import user as userdbq
from logic.db_queries import verification_token as vertokdbq

user_access_bp = Blueprint('user_access', __name__)

@user_access_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    On GET it provides the user login form.
    On POST it verifies the credentials and on success sets `user_id` in session.
    """
    if request.method == 'GET':
        return render_template('user_access.html', access='login', public=True)
    if not userval.validate_login_data(request.form):
        flash('missing_input_msg', 'danger')
        return render_template('user_access.html', access='login', public=True)
    email = request.form.get('email', type=str)
    password = request.form.get('password', type=str)
    user = userdbq.get_user_by_email(email)
    if user is None or not user.check_password(password) or user.deactivated_status(True):
        flash('incorrect_credentials_msg', 'danger')
        return render_template('user_access.html', access='login', public=True)
    if user.banned_status(True):
        flash('banned_user_msg', 'info')
        return render_template('user_access.html', access='login', public=True)
    session['user_id'] = user.id
    return redirect(url_for('home.index'))

@user_access_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Handles user registration.
    On GET it provides the user registration form.
    On POST it validates the credentials and verifies the email availability.
    If successful it creates new user and set `user_id` to session.
    """

    # GET
    if request.method == 'GET':
        return render_template('user_access.html', access='registration', public=True)

    # validation
    result = userval.validate_registration_data(request.form)
    if not result.is_valid():
        email = request.form.get('email', type=str)
        flash('invalid_form_input_msg', 'danger')
        return render_template('user_access.html', access='registration', public=True,
                               email=email, validation_result=result)

    # credentials verification
    email = request.form.get('email', type=str)
    password = request.form.get('password', type=str)
    user = userdbq.get_user_by_email(email)
    if user is not None and user.deactivated_status(False):
        flash('user_already_exists_msg', 'danger')
        return render_template('user_access.html', access='registration', password=password, public=True)
    if user is None:
        user = userdbq.create_user(email, password, 'en')
    else:
        userdbq.set_user_unverified(user)

    # loging-in
    session['user_id'] = user.id
    return redirect(url_for('home.index'))

@user_access_bp.route('/email-verification', defaults={'token': None}, methods=['GET'])
@user_access_bp.route('/email-verification/<token>', methods=['GET'])
def verification(token):
    """
    Handles user email verification. User is required to be logged in.
    On token provided: it validates the token, if valid the token is then verified.
    If succesful the `user_id` is set in session.
    Otherwise: it returns information page that asks user to verify themselves via link sent to email.

    :param token: Verification token encoded in url-safe base64 format.
    """

    # token validation
    if token is not None and not userval.is_token_valid(token):
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('home.index'))

    # logged-in user requirement check
    if 'user_id' not in session:
        flash('login_for_verification_msg', 'warning')
        return redirect(url_for('user_access.login'))

    user = userdbq.get_user_by_id(session['user_id'])

    # user already verified
    if user.unverified_status(False):
        return redirect(url_for('home.index'))


    verification_token = vertokdbq.get_verification_token_by_userid(user.id)
    if verification_token is None:
        # handle not-issued token
        if token is None:
            encoded_token = generate_user_verification_token(user.id, 128)
            return render_template('email_verification.html', token=encoded_token, public=True)
        else:
            decoded_token = decode_base64(token)
            verification_token = vertokdbq.get_verification_token(decoded_token, public=True)
    else:
        # handle issued token
        if token is None:
            encoded_token = encode_base64(verification_token.code)
            return render_template('email_verification.html', token=encoded_token, public=True)
        decoded_token = decode_base64(token)

    # token verification (correctness and expiration)
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
    """
    Handles user password recovery, email prompt.
    On GET it serves a page with email prompt.
    On POST it checks the validity and verifies the existence of the email.
    If successful it notifies the user to verify themselves via the link sent to their email.

    :param user_id:
    :param token: Verification token encoded in url-safe base64 format.
    """

    # GET
    if request.method == 'GET':
        return render_template('user_access.html', access='password_recovery_email', public=True)

    # email validation
    email = request.form.get('email', type=str)
    if not userval.is_email_valid(email):
        flash('invalid_email_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_email', public=True)

    # email verification
    user = userdbq.get_user_by_email(email)
    if user is None:
        flash('incorrect_email_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_email', public=True)

    # delete unverified user
    verification_token = vertokdbq.get_verification_token_by_userid(user.id)
    if user.unverified_status(True):
        if verification_token is not None:
            vertokdbq.delete_verification_token(verification_token)
        userdbq.delete_user(user)
        flash('unverified_account_deleted_msg', 'warning')
        return redirect(url_for('user_access.login'))

    # token handling
    if verification_token is None:
        encoded_token = generate_user_verification_token(user.id, 128)
    else:
        encoded_token = encode_base64(verification_token.code)

    return render_template('password_recovery_verification.html', public=True,
                           user_id=user.id, token=encoded_token)

@user_access_bp.route('/password-recovery/<int:user_id>/<token>', methods=['GET', 'POST'])
def password_recovery_prompt(user_id, token):
    """
    Handles user password recovery, new password prompt.
    On GET it validates the token, if valid it verifies it against the user with given id.
    If successful, the password prompt is shown.
    On POST it validates the password and if valid it sets the password for the user and set `user_id` in session.

    :param user_id:
    :param token: Verification token encoded in url-safe base64 format.
    """

    # token validation
    if not userval.is_token_valid(token):
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('home.index'))

    # user-token possession verification
    user = userdbq.get_user_by_id(user_id)
    verification_token = vertokdbq.get_verification_token_by_userid(user_id)
    if user is None or verification_token is None:
        # if token is None it is a suspicious, might be good to notify the user
        flash('user_could_not_be_verified_msg', 'danger')
        return redirect(url_for('user_access.login'))

    # token verification
    decoded_token = decode_base64(token)
    if verification_token.code != decoded_token:
        flash('invalid_verification_token_msg', 'danger')
        return redirect(url_for('user_access.login'))

    # expiration check
    if verification_token.has_expired():
        vertokdbq.delete_verification_token(verification_token)
        flash('expired_verification_token_msg', 'danger')
        return redirect(url_for('user_access.login'))

    # GET
    if request.method == 'GET':
        return render_template('user_access.html', access='password_recovery_password', public=True,
                               user_id=user.id, token=token)

    # new password validation
    result = userval.validate_password(request.form)
    if not result.is_password_valid():
        flash('invalid_form_input_msg', 'danger')
        return render_template('user_access.html', access='password_recovery_password', public=True,
                               user_id=user.id, token=token, validation_result=result)

    # setting new password and logging-in user
    password = request.form.get('password', type=str)
    userdbq.set_user_password(user, password)
    vertokdbq.delete_verification_token(verification_token)
    session['user_id'] = user.id

    flash('new_password_set_msg', 'success')
    return redirect(url_for('home.index'))
