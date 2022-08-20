from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import click

engine = create_engine(
    'sqlite:///instance/app.sqlite')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    # Create first administrator, does not need
    # oauth2 sign in flow
    db_session.add(app.models.User(user_name='Marduk',
                                   name='Marduk', surname='', administrator=True))
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
