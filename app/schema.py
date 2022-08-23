from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from app.models import (
    User,
    Customer,
    Role
)


class RoleSchema(SQLAlchemySchema):
    class Meta:
        model = Role
        load_instance = True
    id = auto_field()
    name = auto_field()


class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
    id = auto_field()
    user_name = auto_field()
    name = auto_field()
    surname = auto_field()
    roles = fields.Method('get_roles')

    def get_roles(self, user):
        roles = []
        role_schema = RoleSchema()
        for r in user.roles:
            roles.append(role_schema.dump(r))
        return roles


class CustomerSchema(SQLAlchemySchema):
    class Meta:
        model = Customer
        load_instance = True
    id = auto_field()
    name = auto_field()
    surname = auto_field()
    photoURL = fields.String(data_key='photo_url')


user_schema = UserSchema()
customer_schema = CustomerSchema()
