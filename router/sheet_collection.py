from flask import (
    abort,
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    send_file,
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
from logic.validation import sheet as sheetval
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
    """
    Handles sheet photography upload. User needs to be authorized.
    On GET, it serves the form.
    On POST it validates the form, process the input, and saves a record in the database,
    as well as the image in `UPLOAD_DIR`
    """

    # user authorization
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))

    # GET
    if request.method == 'GET':
        return render_template('sheet_collection.html')

    # validation
    result = sheetval.validate_sheet_collection_data(request.form)
    if not result.is_valid():
        flash('invalid_sheet_collection_input_msg', 'danger')
        return render_template('sheet_collection.html', validation_result=result)
    if 'sheet' not in request.files:
        flash('unable_to_upload_the_file_msg', 'danger')
        return render_template('sheet_collection.html')

    # processing and saving
    sheet_file = request.files['sheet']
    light_condition = request.form.get('light-condition', type=str)
    quality = request.form.get('quality', type=str)
    sheet_filename = secure_filename(sheet_file.filename)
    sheet = create_sheet_record(sheet_filename, light_condition, quality, user.id)
    sheet_file.save(f"{UPLOAD_DIR}/{sheet.image_name}")

    flash('sheet_uploaded_success_msg', 'success')
    return render_template('sheet_collection.html')

@sheet_collection_bp.route('/sheet-collection/overview', defaults={'page': 1}, methods=['GET'])
@sheet_collection_bp.route('/sheet-collection/overview/<int:page>', methods=['GET'])
def overview(page):
    """
    Handles sheet photographies overview. User needs to be authorized.
    For given page it serves a relative pagination.

    :param page: Page number to show of sheet records uploaded by the user.
    """

    # user authorization
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))

    # sheet overview with pagination
    page_count = get_pages(PAGE_RECORD_COUNT)
    pages = generate_pagination(page_count, VISIBLE_PAGES, page)
    records = get_page_records(user.id, page - 1, PAGE_RECORD_COUNT)
    return render_template('sheet_collection_overview.html', page=page, records=records, pages=pages)

@sheet_collection_bp.route('/sheet-collection/sheet-image/<image_name>', methods=['GET'])
def image(image_name):
    """
    Handles sheet photography image request. User needs to be authorized.
    For given image name it serves the image from the `UPLOAD_DIR`.

    :param image_name: Unique image name issued by the application.
    """

    # user authorization
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))

    # serving the image file
    if not sheetdbq.sheet_with_uploader_by_image_name(user.id, image_name):
        abort(404)
    image_path = os.path.join(UPLOAD_DIR, image_name)
    if not os.path.isfile(image_path):
        abort(404)
    return send_file(image_path)

@sheet_collection_bp.route('/sheet-collection/delete/<int:record_id>', methods=['GET'])
def delete(record_id):
    """
    Handles sheet record deletion request. User needs to be authorized.
    For given record ID it deletes the record as well as the related image from `UPLOAD_DIR`.

    :param record_id: Sheet record ID.
    """

    # user authorization
    if 'user_id' not in session:
        return redirect(url_for('home.index'))
    user = userdbq.get_user_by_id(session['user_id'])
    if user.unverified_status(True):
        return redirect(url_for('home.index'))

    # deletion
    sheet = sheetdbq.get_uploader_sheet_by_id(user.id, record_id)
    if sheet is None:
        flash('non-existing_sheet_msg', 'danger')
    else:
        sheet_image_path = f"{UPLOAD_DIR}/{sheet.image_name}"
        if os.path.exists(sheet_image_path):
            os.remove(sheet_image_path)
        sheetdbq.delete_sheet(sheet)
        flash('sheet_successfully_deleted_msg', 'success')
    return redirect(url_for('sheet_collection.overview'))
