"""
The aurori project

Copyright (C) 2022  Marcus Drobisch,

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Marcus Drobisch"]
__contact__ = "aurori@fabba.space"
__credits__ = []
__license__ = "AGPLv3+"

from aurori import db, bcrypt
import hashlib
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy_utils import ArrowType
import arrow

users_delegation = db.Table(
    'users_delegation',
    db.Column('delegated_from', db.Integer, db.ForeignKey('users.id')),
    db.Column('delegated_to', db.Integer, db.ForeignKey('users.id')))


class User(db.Model):
    __tablename__ = 'users'
    # nonvolatile data stored in the db
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _password_hash = db.Column(db.LargeBinary(60), nullable=False)
    _pin_hash = db.Column(db.LargeBinary(60))
    _salt = db.Column(db.String(128))
    _api_key_hash = db.Column(db.String(256), nullable=True, default=None)
    email = db.Column(db.String(120), index=True, unique=True)
    firstname = db.Column(db.String(64), default="")
    lastname = db.Column(db.String(64), default="")
    organization = db.Column(db.String(64), default="")
    phone = db.Column(db.String(64), default="")
    orderlimit = db.Column(db.Integer, default=0)
    account_created_date = db.Column(ArrowType, default=arrow.utcnow)
    last_login_date = db.Column(ArrowType, default=arrow.utcnow)
    password_reset_expired_date = db.Column(ArrowType, default=arrow.utcnow)
    password_reset_hash = db.Column(db.String(128), default="")
    account_verified = db.Column(db.Boolean, default=False)
    account_locked = db.Column(db.Boolean, default=False)
    ldap = db.Column(db.Boolean, default=False)
    ldap_dn = db.Column(db.String(64), default="")
    ldap_username = db.Column(db.String(64), default="")
    admin = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Float, default=0)  # fixme: what is this used for?
    delegation = db.relationship(
        'User',
        secondary=users_delegation,
        primaryjoin=(users_delegation.c.delegated_from == id),
        secondaryjoin=(users_delegation.c.delegated_to == id),
        backref=db.backref('delegator', lazy='dynamic'),
        lazy='dynamic')

    sessionToken = db.String(128)  # volatiledata will be reset after restart
    sessionValid = db.Column(
        db.Boolean, default=False)  # volatiledata will be reset after restart
    pinAttempts = db.Integer()
    loginAttempts = db.Integer()

    def __init__(self, email, password, isAdmin=False, skip_password=False):
        self.email = email
        if skip_password is False:
            self.password = password
        self.admin = isAdmin

    def __repr__(self):
        return '<User {} {} : {}>'.format(self.firstname, self.lastname,
                                          self.email)

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plaintext_password):
        self._password_hash = bcrypt.generate_password_hash(plaintext_password)

    @hybrid_method
    def checkPassword(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)

    @hybrid_property
    def api_key(self):
        return self._api_key_hash

    @api_key.setter
    def api_key(self, plaintext_api_key):
        self._api_key_hash = hashlib.sha512(
            plaintext_api_key.encode('utf8')).hexdigest()

    @hybrid_method
    def check_api_key(self, plaintext_api_key):
        return hashlib.sha512(plaintext_api_key).hexdigest() == self.api_key

    @hybrid_property
    def pin(self):
        return self._pin_hash

    @pin.setter
    def pin(self, plaintext_pin):
        self._pin_hash = bcrypt.generate_password_hash(plaintext_pin)

    # checks if user has a certain permission
    @hybrid_method
    def has_permission(self, permission_to_check):
        for permission_group in self.permission_groups:
            for permission in permission_group.permissions:
                if type(permission_to_check) is str:
                    permission_key = permission_to_check
                else:
                    permission_key = str(permission_to_check.__module__).split(
                        '.')[1] + '.' + permission_to_check.__name__
                if permission.name == permission_key:
                    return True
        return False

    @property
    def delegation_user_id(self):
        try:
            return self.delegation.first().id
        except Exception:
            return None
