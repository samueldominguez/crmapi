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
import requests

customer_bp = Blueprint('customer', __name__)


def handle_photoURL(photoURL, req, app):
    """
    Handles user profile picture, saving it to the filesystem
    and returning an URL, whether acquired by providing a URL
    or by sending an actual file

    Returns (URL, None) if successful, (None, error_str) if unsuccessful
    """
    # len('http://') = 7
    # basic validation of URL
    if not photoURL or len(photoURL) <= 7 or 'http' not in photoURL:
        # we need to resort to files in the req
        if 'file' not in req.files:
            return (None, "need either a valid URL in parameter 'photoURL' or an image in the req")
        file = req.files['file']
        if file.filename.strip() == '' or not allowed_file(file.filename):
            return (None, 'filename is not valid. Allowed extensions: {}'.format(app.config.get('ALLOWED_EXTENSIONS')))
        # filename seems OK
        filename = secure_filename(file.filename)
        filename = '{}.{}'.format(secrets.token_urlsafe(64),
                                  filename.split('.')[-1])
        file.save(os.path.join(
            app.config['IMG_UPLOAD_FOLDER'], filename))
        photoURL = url_for('static', filename=os.path.join(app.config.get(
            'IMG_UPLOAD_FOLDER_RELATIVE_STATIC'), filename), _external=True)
    else:
        resp = requests.get(photoURL)
        if resp.status_code < 200 or resp.status_code > 299:
            return (None, "error downloading photo from url '{}'".format(photoURL))
        # generate filename, write to static content and set user's ID
        url_img_extension = photoURL.split('.')[-1]
        filename = '{}.{}'.format(
            secrets.token_urlsafe(64), url_img_extension)
        if not allowed_file(filename):
            return (None, "file extension '{}' is not valid".format(url_img_extension))
        # write to disk
        open(os.path.join(
            app.config['IMG_UPLOAD_FOLDER'], filename), mode='wb').write(resp.content)
        photoURL = url_for('static', filename=os.path.join(app.config.get(
            'IMG_UPLOAD_FOLDER_RELATIVE_STATIC'), filename), _external=True)
    return (photoURL, None)


@customer_bp.route('/customers', methods=['POST'])
@token_auth.login_required
def customer_add():
    created_by_id = token_auth.current_user().id
    name = request.args.get('name')
    surname = request.args.get('surname')
    photoURL = request.args.get('photoURL')
    (photoURL, err) = handle_photoURL(photoURL, request, current_app)
    if err:
        return bad_req_handler(err)
    customer = Customer(created_by_id, name, surname, photoURL)
    with db_session() as session:
        session.add(customer)
        session.commit()
        return jsonify(customer_schema.dump(customer)), 201


@customer_bp.route('/customers/<int:id>', methods=['PUT'])
@token_auth.login_required
def customer_update(id):
    last_updated_by_id = token_auth.current_user().id
    name = request.args.get('name')
    surname = request.args.get('surname')
    photoURL = request.args.get('photoURL')

    # Get the customer to update
    customer = db_session.query(Customer).filter(Customer.id == id).first()

    if not customer:
        return bad_req_handler("user with id {} does not exist".format(id))

    if name:
        customer.name = name
    if surname:
        customer.surname = surname
    if photoURL:
        (photoURL, err) = handle_photoURL(photoURL, request, current_app)
        if err:
            return bad_req_handler(err)
        else:
            customer.photoURL = photoURL
    return jsonify(customer_schema.dump(customer)), 200


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
