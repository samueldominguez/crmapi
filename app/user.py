from flask import (
    Blueprint,
    jsonify,
    request
)
from app.auth import (
    token_auth,
    authorize_roles
)
from app.schema import user_schema
from app.db import db_session
from app.models import User, Role
import logging


def bad_req_handler(error):
    """Return the error as json and status code 400"""
    return jsonify({'error': error}), 400


user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['POST'])
@token_auth.login_required
@authorize_roles(['admin'])
def user_add():
    user_name = request.args.get('user_name')
    password = request.args.get('password')
    name = request.args.get('name', '')
    surname = request.args.get('surname', '')
    roles = request.args.get('roles', '')

    if user_name is None or password is None:
        return bad_req_handler("'user_name' and 'password' are required parameters")

    if roles is not None:
        # clean up roles format
        roles = {role.strip().lower()
                 for role in roles.split(',') if len(role.strip().lower()) > 0}
        # check each role exists
        current_roles = {role.name for role in db_session.query(Role).all()}
        if not all([role in current_roles for role in roles]):
            return bad_req_handler("provided roles do not all exist")

    new_user = User(user_name, password, name,
                    surname, [role for role in roles])
    try:
        db_session.add(new_user)
        db_session.commit()
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        logging.info(message)
    return jsonify(user_schema.dump(new_user)), 201


@ user_bp.route('/users/<int:id>', methods=['PUT'])
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_update(id):
    pass


@ user_bp.route('/users/<int:id>', methods=['DELETE'])
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_delete(id):
    pass


@ user_bp.route('/users/<int:id>')
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_get(id):
    logging.info('blah')
    return jsonify(user_schema.dump(db_session.query(User).filter(User.id == id).first()))


@ user_bp.route('/users')
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_list():
    pass
