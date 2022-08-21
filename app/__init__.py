from flask import Flask, request

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

    # Authentication
    token_auth = HTTPTokenAuth()

    @ app.route('/customers', methods=['POST'])
    def customer_add():
        pass

    @ app.route('/customers/<int:id>', methods=['PUT'])
    def customer_update(id):
        pass

    @ app.route('/customers/<int:id>', methods=['DELETE'])
    def customer_delete(id):
        pass

    @ app.route('/customers/<int:id>')
    def customer_get(id):
        pass

    @ app.route('/customers')
    def customer_list():
        pass

    @ app.route('/users', methods=['POST'])
    def user_add():
        pass

    @ app.route('/users/<int:id>', methods=['PUT'])
    def user_update(id):
        pass

    @ app.route('/users/<int:id>', methods=['DELETE'])
    def user_delete(id):
        pass

    @ app.route('/users/<int:id>')
    def user_get(id):
        pass

    @ app.route('/users')
    def user_list():
        pass

    @ app.route('/')
    def root():
        logging.info('root handler called')
        return '<h1>CRM API</h1><p>Welcome to the CRM API</p>'

    @ app.route('/hello')
    def hello():
        return 'Hello, flask!'

    return app
