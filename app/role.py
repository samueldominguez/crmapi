from flask import (
    Blueprint,
    jsonify
)
from app.auth import (
    token_auth,
    authorize_roles
)
from app.schema import user_schema
from app.db import db_session
from app.models import Role

role_bp = Blueprint('role', __name__)


@role_bp.route('/users', methods=['POST'])
@token_auth.login_required
@authorize_roles(['admin'])
def user_add():
    user = token_auth.current_user()
    return 'cool, u are an admin'


@ role_bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
@authorize_roles(['admin'])
def user_update(id):
    pass


@ role_bp.route('/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
@authorize_roles(['admin'])
def user_delete(id):
    pass


@ role_bp.route('/users/<int:id>')
@token_auth.login_required
@authorize_roles(['admin'])
def user_get(id):
    return jsonify(user_schema.dump(db_session.query(User).filter(User.id == id).first()))


@ role_bp.route('/users')
@token_auth.login_required
@authorize_roles(['admin'])
def user_list():
    pass
