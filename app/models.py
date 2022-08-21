from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db import Base
import secrets
from argon2 import PasswordHasher

ph = PasswordHasher()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(30), unique=True)
    name = Column(String(50))
    surname = Column(String(50))
    administrator = Column(Boolean(), default=False)
    salt = Column(String(43))
    password_hash = Column(String(16))

    def __init__(self, user_name, password, name='', surname='', administrator=False):
        self.user_name = user_name
        self.name = name
        self.surname = surname
        self.administrator = administrator
        self.salt = secrets.token_urlsafe()
        self.password_hash = ph.hash(self.salt + password)

    def __repr__(self):
        return "{}: name: {} surname: {} administator: {} len(refresh_token): {}".format(self.user_name, self.name, self.surname, self.administrator, len(self.refresh_token))


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

    def __repr__(self):
        return "{}: name: {} surname: {} photoURL: {} creator: {} updated by: {}".format(self.id, self.name, self.surname, self.photoURL, self.created_by_id, self.last_updated_by_id)
