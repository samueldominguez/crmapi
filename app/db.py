from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import click
import os
import logging

ENV = os.getenv('ENV')
if ENV == 'DEV':
    import config_dev as config
else:
    import config_prod as config

engine = create_engine(
    'sqlite:///' + os.path.join(config._DATABASE_FOLDER, config._DATABASE_NAME))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    # Check if the database already has content
    # Create roles
    admin_role = app.models.Role('admin')
    wizard_role = app.models.Role('wizard')
    db_session.add(admin_role, wizard_role)
    # Create first admin, and a normal user
    marduk_password = 'universe' if ENV == 'DEV' else config.ADMIN_PROD_PASSWORD
    marduk = app.models.User('marduk', marduk_password,
                             name='Marduk', surname='Babylonian', roles=[admin_role, wizard_role])
    db_session.add(marduk)
    if ENV == 'DEV':
        human = app.models.User('human', 'earth',
                                name='Human', surname='Earthling', administrator=False, roles=[wizard_role])

        db_session.add(human)
    logging.info("Created some stuff son")
    db_session.commit()


def close_db(exception=None):
    db_session.remove()


@click.command('init-db')
def init_db_command():
    """Create database from scratch"""
    init_db()
    click.echo('Created the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    if not engine.has_table('user'):
        logging.info("Database has not been initialized")
        logging.info("Creating database...")
        init_db()
        logging.info('Created the database')
    else:
        logging.info('Database exists already, not regenerating')
