from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic.helpers import create_sheet_record
from logic.db_queries import user as userdbq
from logic.db_queries import sheet as sheetdbq
from werkzeug.utils import secure_filename

sheet_collection_bp = Blueprint('sheet_collection', __name__)

UPLOAD_DIR = None

def set_upload_directory(directory: str):
    global UPLOAD_DIR
    UPLOAD_DIR = directory

@sheet_collection_bp.route('/sheet-collection', methods=['GET', 'POST'])
def sheet_collection():
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    if request.method == 'GET':
        return render_template('sheet_collection.html')
    print(request.form)
    print(request.files)
    light_condition = request.form.get('light-condition', type=str)
    quality = request.form.get('quality', type=str)
    if 'sheet' not in request.files:
        flash('unable_to_upload_the_file_msg', 'danger')
        return render_template('sheet_collection.html')
    sheet_file = request.files['sheet']
    sheet_filename = secure_filename(sheet_file.filename)
    create_sheet_record(sheet_filename, light_condition, quality, user.id)
    sheet_file.save(f"{UPLOAD_DIR}/{sheet_filename}")
    flash('sheet_uploaded_success_msg', 'success')
    return render_template('sheet_collection.html')

@sheet_collection_bp.route('/sheet-collection-overview', methods=['GET'])
def sheet_collection_overview():
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    if request.method == 'GET':
        return render_template('sheet_collection.html')
    print(request.form)
    print(request.files)
    light_condition = request.form.get('light-condition', type=str)
    quality = request.form.get('quality', type=str)
    if 'sheet' not in request.files:
        flash('unable_to_upload_the_file_msg', 'danger')
        return render_template('sheet_collection.html')
    sheet_file = request.files['sheet']
    sheet_filename = secure_filename(sheet_file.filename)
    create_sheet_record(sheet_filename, light_condition, quality, user.id)
    sheet_file.save(f"{UPLOAD_DIR}/{sheet_filename}")
    flash('sheet_uploaded_success_msg', 'success')
    return render_template('sheet_collection.html')
