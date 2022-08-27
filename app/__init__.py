from flask import Flask
from logging.config import dictConfig
import logging
import os
import bleach


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
    app = Flask(__name__,
                static_folder='../static')
    logging.info('Creating application')
    EXEC_ENV = os.getenv("ENV")
    if EXEC_ENV == 'DEV':
        logging.info("Running in development environment")
        app.config.from_pyfile('../config_dev.py', silent=True)
    elif EXEC_ENV == 'PROD':
        logging.info("Running in production environment")
        app.config.from_pyfile('../config_prod.py', silent=True)
    else:
        logging.error(
            'EXEC_ENV environment variable not configured to values DEV or PROD, exiting...')
        return

    # Initialize database
    logging.info('Initializing database...')
    import app.db as db
    db.init_app(app)
    logging.info('Database initialized')

    # v1 api prefix
    v1_prefix = '/api/v1/'

    # Authentication
    from app.auth import auth_bp

    logging.info('Registering authentication endpoints...')
    app.register_blueprint(auth_bp, url_prefix=v1_prefix + 'auth/')
    logging.info('Authentication endpoints registered')

    # Application routes
    from app.user import user_bp
    from app.customer import customer_bp

    logging.info('Registering application endpoints...')
    app.register_blueprint(user_bp, url_prefix=v1_prefix)
    app.register_blueprint(customer_bp, url_prefix=v1_prefix)
    logging.info('Application endpoints registered')

    # To prevent XSS, setting Content-Type to application/json should do the trick for most
    # modern browsers, but some may still sniff
    # the response and guess content type based on
    # that, to prevent that we set the
    # X-Content-Type-Options header to nosniff
    # so the browser respects Content-Type
    @app.after_request
    def apply_security_measures(response):
        """
        Cleans responses from potential XSS attacks with bleach
        Adds header to ask browsers not to guess content type and
        follow the content-type header
        """
        if response.content_type in ['text/html', 'application/json']:
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.set_data(bleach.clean(response.get_data(as_text=True)))
        return response

    @ app.route('/')
    def root():
        logging.info('root handler called')
        return '<h1>CRM API</h1><p>Welcome to the CRM API</p>'

    logging.info('Application created.')
    return app
