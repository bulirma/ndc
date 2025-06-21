from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from logic.db_queries import sheet as sheetdbq

sheet_collection_bp = Blueprint('sheet_collection', __name__)

@sheet_collection_bp.route('/sheet-collection', methods=['GET', 'POST'])
def sheet_collection():
    if 'user_id' not in session:
        return render_template('index.html')
    if request.method == 'GET':
        return render_template('sheet_collection.html')
    print(request.form)
    return render_template('sheet_collection.html')
