from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db import Base
import secrets
from argon2 import PasswordHasher

ph = PasswordHasher()

user_roles_table = Table('user_roles', Base.metadata,
                         Column('user_id', ForeignKey('user.id')),
                         Column('role_id', ForeignKey('role.id')),
                         )


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(30), unique=True)
    name = Column(String(50))
    surname = Column(String(50))
    salt = Column(String(43))
    password_hash = Column(String(16))
    roles = relationship('Role', secondary=user_roles_table)

    def __init__(self, user_name, password, name='', surname='', roles=[]):
        self.user_name = user_name
        self.name = name
        self.surname = surname
        self.salt = secrets.token_urlsafe()
        self.password_hash = ph.hash(self.salt + password)
        self.roles = roles


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    photoURL = Column(String(100))
    created_by_id = Column(Integer, ForeignKey("user.id"))
    last_updated_by_id = Column(Integer, ForeignKey("user.id"))
    created_by = relationship('User', foreign_keys=[
                              created_by_id])
    last_updated_by = relationship(
        'User', foreign_keys=[last_updated_by_id])

    def __init__(self, created_by_id, name='', surname='', photoURL=''):
        self.created_by_id = created_by_id
        self.last_updated_by_id = created_by_id
        self.name = name
        self.surname = surname
        self.photoURL = photoURL


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)

    def __init__(self, name):
        self.name = name
