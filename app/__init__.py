from flask import Flask, Response, request, jsonify
from app.models import User, Customer
from logging.config import dictConfig
import logging
import os


def create_app(test_config=None):
    # Set up logging handlers, one for stderr and a rotating one to file
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
            'filehandler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': 'logs/app.log',
            'backupCount': 5,
            'maxBytes': 1_000_000
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'filehandler']
        }
    })

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    import app.db as db
    from app.db import db_session
    db.init_app(app)

    # Marshmallow schemas for deserialization
    from app.schema import user_schema, customer_schema

    # Authentication
    from app.auth import token_auth, auth_bp, authorize_roles

    app.register_blueprint(auth_bp)

    @ app.route('/customers', methods=['POST'])
    @token_auth.login_required
    def customer_add():
        return jsonify({'user_name': token_auth.current_user().user_name})

    @ app.route('/customers/<int:id>', methods=['PUT'])
    @token_auth.login_required
    def customer_update(id):
        pass

    @ app.route('/customers/<int:id>', methods=['DELETE'])
    @token_auth.login_required
    def customer_delete(id):
        pass

    @ app.route('/customers/<int:id>')
    @token_auth.login_required
    def customer_get(id):
        return customer_schema(db_session.query(Customer).filter(Customer.id == id).first())

    @ app.route('/customers')
    @token_auth.login_required
    def customer_list():
        pass

    @ app.route('/users', methods=['POST'])
    @token_auth.login_required
    @authorize_roles(['admin'])
    def user_add():
        user = token_auth.current_user()
        return 'cool, u are an admin'

    @ app.route('/users/<int:id>', methods=['PUT'])
    @token_auth.login_required
    @authorize_roles(['admin'])
    def user_update(id):
        pass

    @ app.route('/users/<int:id>', methods=['DELETE'])
    @token_auth.login_required
    @authorize_roles(['admin'])
    def user_delete(id):
        pass

    @ app.route('/users/<int:id>')
    @token_auth.login_required
    @authorize_roles(['admin'])
    def user_get(id):
        return jsonify(user_schema.dump(db_session.query(User).filter(User.id == id).first()))

    @ app.route('/users')
    @token_auth.login_required
    @authorize_roles(['admin'])
    def user_list():
        pass

    @ app.route('/')
    def root():
        logging.info('root handler called')
        return '<h1>CRM API</h1><p>Welcome to the CRM API</p>'

    return app
