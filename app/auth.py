from flask import (
    Blueprint,
    jsonify
)
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from argon2 import PasswordHasher
import jwt
from app.db import db_session
from app.models import User
from datetime import datetime, timedelta, timezone

bp = Blueprint('auth', __name__, url_prefix='/auth')
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
ph = PasswordHasher()


@basic_auth.verify_password
def verify_password(user, password):
    """Verify password against database hashes"""
    u = db_session.query(User).filter(User.user_name == user).first()
    if ph.verify(u.salt + u.password_hash, password):
        return u


@token_auth.verify_token
def verify_token(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return db_session.query(User).filter(User.id == payload['user_id']).first()
    except:
        return False


@bp.route('/tokens', methods=['POST'])
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
    jsonify({
        'token': token,
        'expiry': expiry.isoformat()
    })
