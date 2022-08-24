from flask import (
    Blueprint,
    jsonify,
    request,
    Response
)
from app.auth import (
    token_auth,
    authorize_roles
)
from app.schema import user_schema
from app.db import db_session
from app.models import User, Role
import logging
from sqlalchemy import exc
from app.utils import bad_req_handler, fill_response_with_pagination_headers


def check_and_sanitize_roles(roles):
    """
    Checks all input roles exist and if there
    are errors, reports back.

    Returns tuple Optional[List[Role]], Optional[str]
    """
    # cleanup bad formatting, using a set to eliminate duplicates
    roles = {role.strip().lower()
             for role in roles.split(',') if len(role.strip().lower()) > 0}
    if len(roles) == 0:
        return (None, 'no roles specified')
    # check each role exists
    all_roles = db_session.query(Role).all()
    all_roles_names = {role.name for role in all_roles}
    if not all([role in all_roles_names for role in roles]):
        return (None, 'not all provided roles exist')
    # get each object and return it
    return ([role for role in all_roles if role.name in roles], None)


user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['POST'])
@token_auth.login_required
@authorize_roles(['admin'])
def user_add():
    user_name = request.args.get('user_name')
    password = request.args.get('password')
    name = request.args.get('name', '')
    surname = request.args.get('surname', '')
    roles = request.args.get('roles', [])

    if user_name is None or password is None:
        return bad_req_handler("'user_name' and 'password' are required parameters")

    if roles:
        (roles, err) = check_and_sanitize_roles(roles)
        if err:
            return bad_req_handler(err)

    new_user = User(user_name, password, name,
                    surname, [role for role in roles])
    try:
        with db_session() as session:
            session.add(new_user)
            session.commit()
            return jsonify(user_schema.dump(new_user)), 201
    except exc.IntegrityError:
        return bad_req_handler('user {} already exists'.format(user_name))


@ user_bp.route('/users/<int:id>', methods=['PUT'])
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_update(id):
    user_name = request.args.get('user_name')
    password = request.args.get('password')
    name = request.args.get('name')
    surname = request.args.get('surname')
    roles = request.args.get('roles')

    # get the user to update
    user = db_session.query(User).filter(User.id == id).first()

    if not user:
        return bad_req_handler('user with id {} does not exist'.format(id))

    if roles:
        (roles, err) = check_and_sanitize_roles(roles)
        if err:
            return bad_req_handler(err)

    if user_name:
        user.user_name = user_name
    if password:
        user.set_password(password)
    if name:
        user.name = name
    if surname:
        user.surname = surname
    if roles:
        user.roles = roles
    db_session.commit()
    return jsonify(user_schema.dump(user)), 200


@ user_bp.route('/users/<int:id>', methods=['DELETE'])
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_delete(id):
    user = db_session.query(User).filter(User.id == id).first()
    if not user:
        return bad_req_handler('user with id {} does not exist'.format(id))
    db_session.delete(user)
    db_session.commit()
    return Response(None, status=204)


@ user_bp.route('/users/<int:id>')
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_get(id):
    user = db_session.query(User).filter(User.id == id).first()
    if not user:
        return bad_req_handler('user with id {} does not exist'.format(id))
    return jsonify(user_schema.dump(user))


@ user_bp.route('/users')
@ token_auth.login_required
@ authorize_roles(['admin'])
def user_list():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
    except ValueError:
        return bad_req_handler("please provide integers for 'page' and 'per_page'")
    total_users = db_session.query(User).count()
    users = db_session.query(User).offset(
        (page-1)*per_page).limit(per_page).all()
    r = jsonify(list(map(lambda x: user_schema.dump(x), users)))
    r = fill_response_with_pagination_headers(
        r, page, per_page, total_users, 'user.user_list', request.args)
    return r
