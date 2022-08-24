from flask import Flask
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

    app = Flask(__name__, instance_relative_config=True,
                static_folder='../static')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        PREFERRED_URL_SCHEME='http',
        SERVER_NAME='127.0.0.1:5000',
        IMG_UPLOAD_FOLDER_RELATIVE_STATIC='images',
        IMG_UPLOAD_FOLDER=os.path.join(app.static_folder, 'images'),
        ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg'},
        JSON_SORT_KEYS=False
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
    db.init_app(app)

    # v1 api prefix
    v1_prefix = '/api/v1/'

    # Authentication
    from app.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix=v1_prefix + 'auth/')

    # Application routes
    from app.user import user_bp
    from app.customer import customer_bp

    app.register_blueprint(user_bp, url_prefix=v1_prefix)
    app.register_blueprint(customer_bp, url_prefix=v1_prefix)

    @ app.route('/')
    def root():
        logging.info('root handler called')
        return '<h1>CRM API</h1><p>Welcome to the CRM API</p>'

    return app
