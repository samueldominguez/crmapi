import os
from flask import Flask, request
from app.models import User, Customer


def create_app(test_config=None):
    # TODO: set instance path via module+relative?
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

    @app.route('/hello')
    def hello():
        return 'Hello, flask!'

    @app.route('/admins')
    def list_admins():
        return repr(db_session.query(User).one())

    @app.route('/customer/add', methods=['POST'])
    def user_add():
        db_session.add(Customer(1, request.args.get('name'), request.args.get(
            'surname'), 'https://img.google.com/ahsdy7YF7'))
        db_session.commit()
        return 'OK'

    @app.route('/customer/list')
    def user_list():
        return repr(db_session.query(Customer).one())

    return app
