from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic.helpers.common import generate_pagination
from logic.helpers.db_queries import (
    create_sheet_record,
    get_pages,
    get_page_records
)
from logic.db_queries import user as userdbq
from logic.db_queries import sheet as sheetdbq
import os
from werkzeug.utils import secure_filename

sheet_collection_bp = Blueprint('sheet_collection', __name__)

UPLOAD_DIR = None
PAGE_RECORD_COUNT = 10
VISIBLE_PAGES = 9

def set_upload_directory(directory: str):
    global UPLOAD_DIR
    UPLOAD_DIR = directory

@sheet_collection_bp.route('/sheet-collection', methods=['GET', 'POST'])
def form():
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    if request.method == 'GET':
        return render_template('sheet_collection.html')
    light_condition = request.form.get('light-condition', type=str)
    quality = request.form.get('quality', type=str)
    if 'sheet' not in request.files:
        flash('unable_to_upload_the_file_msg', 'danger')
        return render_template('sheet_collection.html')
    sheet_file = request.files['sheet']
    sheet_filename = secure_filename(sheet_file.filename)
    sheet = create_sheet_record(sheet_filename, light_condition, quality, user.id)
    sheet_file.save(f"{UPLOAD_DIR}/{sheet.image_name}")
    flash('sheet_uploaded_success_msg', 'success')
    return render_template('sheet_collection.html')

@sheet_collection_bp.route('/sheet-collection/overview', defaults={'page': 1}, methods=['GET'])
@sheet_collection_bp.route('/sheet-collection/overview/<int:page>', methods=['GET'])
def overview(page):
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    page_count = get_pages(PAGE_RECORD_COUNT)
    pages = generate_pagination(page_count, VISIBLE_PAGES, page)
    records = get_page_records(user.id, page - 1, PAGE_RECORD_COUNT)
    return render_template('sheet_collection_overview.html', page=page, records=records, pages=pages)

#@sheet_collection_bp.route('/sheet-collection/sheet-image/<image_name>', methods=['GET'])
#def image(image_name):
#    pass

@sheet_collection_bp.route('/sheet-collection/delete/<int:record_id>', methods=['GET'])
def delete(record_id):
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))
    sheet = sheetdbq.get_sheet_by_id(record_id)
    if sheet is None:
        flash('non-existing_sheet_msg', 'danger')
    else:
        # TODO: error handling
        os.remove(f"{UPLOAD_DIR}/{sheet.image_name}")
        sheetdbq.delete_sheet(sheet)
        flash('sheet_successfully_deleted_msg', 'success')
    return redirect(url_for('sheet_collection.overview'))
