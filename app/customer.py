from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    url_for
)
from app.auth import (
    token_auth
)
from werkzeug.utils import secure_filename
from app.schema import customer_schema
from app.db import db_session
from app.models import Customer
from app.utils import bad_req_handler, fill_response_with_pagination_headers, allowed_file
import os
import secrets
from sqlalchemy import exc

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/customers', methods=['POST'])
@token_auth.login_required
def customer_add():
    # req: created_by_id
    # opt: name, surname, photoURL
    created_by_id = token_auth.current_user().id
    name = request.args.get('name')
    surname = request.args.get('surname')
    photoURL = request.args.get('photoURL')

    # len('http://') = 7
    # basic validation of URL
    if not photoURL or len(photoURL) <= 7 or 'http' not in photoURL:
        # we need to resort to files in the request
        if 'file' not in request.files:
            return bad_req_handler("need either a valid URL in parameter 'photoURL' or an image in the request")
        file = request.files['file']
        if file.filename.strip() == '' or not allowed_file(file.filename):
            return bad_req_handler('filename is not valid. Allowed extensions: {}'.format(current_app.config.get('ALLOWED_EXTENSIONS')))
        # filename seems OK
        filename = secure_filename(file.filename)
        filename = '{}.{}'.format(secrets.token_urlsafe(64),
                                  filename.split('.')[-1])
        file.save(os.path.join(
            current_app.config['IMG_UPLOAD_FOLDER'], filename))
        photoURL = url_for('static', filename=os.path.join(current_app.config.get(
            'IMG_UPLOAD_FOLDER_RELATIVE_STATIC'), filename), _external=True)
    else:
        # the URL seems OK, try to download the picture
        pass
    customer = Customer(created_by_id, name, surname, photoURL)
    with db_session() as session:
        session.add(customer)
        session.commit()
        return jsonify(customer_schema.dump(customer)), 201


@customer_bp.route('/customers/<int:id>', methods=['PUT'])
@token_auth.login_required
def customer_update(id):
    pass


@customer_bp.route('/customers/<int:id>', methods=['DELETE'])
@token_auth.login_required
def customer_delete(id):
    pass


@customer_bp.route('/customers/<int:id>')
@token_auth.login_required
def customer_get(id):
    return customer_schema(db_session.query(Customer).filter(Customer.id == id).first())


@customer_bp.route('/customers')
@token_auth.login_required
def customer_list():
    pass
