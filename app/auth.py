from flask import (
    Blueprint,
    jsonify,
    Response
)
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from functools import wraps
from argon2 import PasswordHasher
import jwt
from app.db import db_session
from app.models import User
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
ph = PasswordHasher()


@basic_auth.verify_password
def verify_password(user, password):
    """Verify password against database hashes"""
    u = db_session.query(User).filter(User.user_name == user).first()
    if u is None:
        return None
    elif ph.verify(u.password_hash, u.salt + password):
        return u


@token_auth.verify_token
def verify_token(token):
    """Verify token and return user ID encoded in JWT token"""
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return db_session.query(User).filter(User.id == payload['user_id']).first()
    except:
        return False


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


@auth_bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def token_get():
    """Generate JWT token after login, should expire 1 hour from generation"""
    expiry = datetime.now(
        tz=timezone.utc) + timedelta(0, 60*60)
    payload = {
        'exp': expiry,
        'user_id': basic_auth.current_user().id
    }
    token = jwt.encode(payload, 'secret')
    return jsonify({
        'token': token,
        'expires_at': expiry.isoformat()
    })
