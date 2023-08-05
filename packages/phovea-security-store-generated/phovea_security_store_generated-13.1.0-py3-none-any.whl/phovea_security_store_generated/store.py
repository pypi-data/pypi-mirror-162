#####################################################################
# Copyright (c) The Caleydo Team, http://caleydo.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#####################################################################


import hashlib
import logging
import sqlite3
import uuid
from functools import lru_cache

from tdp_core.security.model import User
from tdp_core.security.store.base_store import BaseStore

from .settings import get_settings

__author__ = "Samuel Gratzl"
_log = logging.getLogger(__name__)


def hash_password(password, salt):
    return hashlib.sha512((password + salt).encode("utf-8")).hexdigest()


def ensure_dir(path):
    import errno
    import os

    path = os.path.dirname(path)
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class FakeUser(User):
    password: str
    salt: str

    def is_password(self, given):
        given_h = hash_password(given, self.salt)
        return given_h == self.password


class FakeStore(BaseStore):
    def __init__(self):
        self._config = get_settings()
        ensure_dir(self._config.file)
        db = self.get_db()
        db.execute(
            """CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, salt TEXT, roles TEXT, creation_date TEXT, last_login_date TEXT)"""
        )
        db.commit()

        self._users = list(self._load_users())

    def get_db(self):
        return sqlite3.connect(self._config.file)

    def _load_users(self):
        for row in self.get_db().execute("""SELECT username, password, salt, roles FROM user"""):
            yield FakeUser(id=row[0], name=row[0], password=row[1], salt=row[2], roles=row[3].split(";"))

    def _flag_logged_in(self, user):
        db = self.get_db()
        db.execute("""UPDATE user SET last_login_date = date('now') WHERE username = ?""", (user.name,))
        db.commit()

    def _persist_user(self, user):
        db = self.get_db()
        db.execute(
            """
INSERT INTO user(username, password, salt, roles, creation_date, last_login_date) VALUES(?,?,?,?,date('now'),date('now'))
""",
            (user.name, user.password, user.salt, ";".join(user.roles)),
        )
        db.commit()

    def logout(self, user):
        pass

    def load_from_key(self, api_key):
        try:
            api_key = api_key.decode()  # Convert to string if bytes-like
        except (UnicodeDecodeError, AttributeError):
            pass

        parts = api_key.split(":")
        if len(parts) != 2:
            return None
        return self.login(parts[0], dict(password=parts[1]))

    def _find_user(self, username, password):
        return next((u for u in self._users if u.id == username and u.is_password(password)), None)

    def login(self, username, extra_fields=None):
        if extra_fields is None:
            extra_fields = {}
        password = extra_fields["password"]

        user = next((u for u in self._users if u.id == username), None)
        if user:
            # existing user
            if user.is_password(password):
                self._flag_logged_in(user)
                return user
            else:
                return None

        # create a new one on the fly given the new values
        user = self._add_user(username, password)
        return user

    def _add_user(self, username, password):
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512((password + salt).encode("utf-8")).hexdigest()
        user = FakeUser(id=username, name=username, password=hashed_password, salt=salt, roles=[username])
        self._users.append(user)
        _log.info("registering new user: " + username)
        self._persist_user(user)
        return user


@lru_cache(maxsize=1)
def create():
    return FakeStore()
