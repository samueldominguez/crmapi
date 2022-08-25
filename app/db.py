from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import click

engine = create_engine(
    'sqlite:///data/app.sqlite')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    # Create roles
    admin_role = app.models.Role('admin')
    wizard_role = app.models.Role('wizard')
    # Create first admin, and a normal user
    marduk = app.models.User('marduk', 'universe',
                             name='Marduk', surname='Babylonian', administrator=True, roles=[admin_role, wizard_role])
    human = app.models.User('human', 'earth',
                            name='Human', surname='Earthling', administrator=False, roles=[wizard_role])
    db_session.add(marduk)
    db_session.add(human)
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
