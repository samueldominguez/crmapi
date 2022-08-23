from flask import (
    Blueprint,
    jsonify,
    request
)
from app.auth import (
    token_auth
)
from app.schema import customer_schema
from app.db import db_session
from app.models import Customer

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/customers', methods=['POST'])
@token_auth.login_required
def customer_add():
    return jsonify({'user_name': token_auth.current_user().user_name})


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
