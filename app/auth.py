from flask import (
    Blueprint,
    jsonify,
    Response,
    request,
    current_app,
    g
)
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from functools import wraps
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from app.db import db_session
from app.models import OAuth2Client, User
from datetime import datetime, timedelta, timezone
import logging

from app.utils import bad_req_handler

auth_bp = Blueprint('auth', __name__, url_prefix='/oauth')
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
oauth_token_auth = HTTPTokenAuth()
multi_auth = MultiAuth(basic_auth, oauth_token_auth)
ph = PasswordHasher()


@basic_auth.verify_password
def verify_password(user, password):
    """Verify password against database hashes"""
    u = db_session.query(User).filter(User.user_name == user).first()
    if u is None:
        return None
    try:
        ph.verify(u.password_hash, u.salt + password)
        g.auth_type = 'basic'
        return u
    except VerifyMismatchError:
        return None


def general_verify_token(token, types=['access_token']):
    try:
        payload = jwt.decode(token, current_app.config.get(
            'SECRET_KEY'), algorithms=['HS256'])
        # check typeis correct
        if payload['type'] not in types:
            return False
        # after correctly decoding the payload from the JWT, we need to store
        # it in 'g' to store some extra information
        g.oauth2_scope = payload['scope'] if 'scope' in payload else ''
        g.auth_type = 'token'
        return db_session.query(User).filter(User.id == payload['user_id']).first()
    except:
        return False


@token_auth.verify_token
def verify_token(token):
    """Verify token and return user ID encoded in JWT token"""
    return general_verify_token(token, ['access_token'])


@oauth_token_auth.verify_token
def verify_token(token):
    return general_verify_token(token, ['access_token', 'refresh_token'])


def authorize_roles(roles):
    """
    Decorator function
    ==================
    Takes in an array of roles, and checks whether the current user
    has any of those roles
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_roles = [r.name for r in token_auth.current_user().roles]
            for r in roles:
                if r in user_roles:
                    return func(*args, **kwargs)
            return Response(response='Unauthorized', status=403)
        return wrapper
    return decorator


@auth_bp.route('/token', methods=['POST'])
@multi_auth.login_required
def token_get():
    """Return access token, refresh token and other information if user authenticates correctly"""
    # user_name+password are valid, now check
    # - client_id exists
    # - grant specified is valid for the client
    # - scopes specified are valid for the client
    client_id = request.args.get('client_id')
    grant = request.args.get('grant', 'password')  # default to password grant
    scope = request.args.get('scope')

    if not client_id or (not scope and grant != 'refresh_token'):
        return bad_req_handler("'client_id' and 'scope' must be specified")

    client = db_session.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id).first()
    if not client:
        return bad_req_handler("client does not exist")
    client_grants = [g.name for g in client.grants]
    if grant not in client_grants:
        return bad_req_handler('client does not have specified grant')
    if grant == 'password' and g.auth_type == 'token':
        return bad_req_handler('password grant requires basic auth')
    elif grant == 'refresh_token' and g.auth_type == 'basic':
        return bad_req_handler('refresh_token grant requires bearer token')
    # check the grant
    if grant == 'refresh_token':
        scope = g.oauth2_scope if hasattr(g, 'oauth2_scope') else ''
    scope = [s.strip().lower() for s in scope.split(',')]
    client_scopes = [s.name for s in client.scopes]
    scope = [x for x in client_scopes if x in scope]
    if not scope:
        return bad_req_handler('client does not have any specified scopes')
    # transform scope back into response format
    scope = ','.join(scope)
    issued_at = int(datetime.now().timestamp())
    # Access token generation
    expires_in = current_app.config.get('OAUTH2_ACCESS_TOKEN_EXPIRY')
    jwt_payload = {
        'exp': issued_at + expires_in,
        'user_id': multi_auth.current_user().id,
        'type': 'access_token'
    }
    token = jwt.encode(jwt_payload, current_app.config.get('SECRET_KEY'))

    # Refresh token generation
    refresh_token_expires_in = current_app.config.get(
        'OAUTH2_REFRESH_TOKEN_EXPIRY')
    refresh_token_jwt_payload = {
        'exp': issued_at + refresh_token_expires_in,
        'user_id': multi_auth.current_user().id,
        'scope': scope,
        'type': 'refresh_token'
    }
    refresh_token = jwt.encode(
        refresh_token_jwt_payload, current_app.config.get('SECRET_KEY'))

    return jsonify({
        'access_token': token,
        'issued_at': issued_at,
        'expires_in': expires_in,
        'token_type': 'BearerToken',
        'scope': scope,
        'grant': grant,
        'client_id': client_id,
        'refresh_token': refresh_token,
        'refresh_token_expires_in': refresh_token_expires_in
    })
