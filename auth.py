"""
Handles user authentication
"""

import db
import bcrypt
from aiohttp import web
import sqlite3
import re

@db.handle
def create_account(cur, session, username, password):
    """
    Creates a new account

    :param cur: the database cursor
    :param session: the current session
    :param username: the new username
    :param password: the new password
    :return: the user
    """
    if re.match("^[\w-]+$", username) is None or len(password) < 6:
        raise web.HTTPBadRequest

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cur.execute(
            "INSERT INTO User (Username, Password) VALUES (?, ?)",
            (username, hashed_password)
        )
    except sqlite3.Error:
        # A user already exists
        raise web.HTTPBadRequest
    else:
        _set_user(session, cur.lastrowid)

@db.handle
def login(cur, session, username, password):
    """Logs in a user"""
    user = cur.execute(
        "SELECT UserID, Password FROM User WHERE Username = ?",
        (username,)
    ).fetchone()
    if user is not None and bcrypt.checkpw(password.encode("utf-8"), user[1]):
        _set_user(session, user[0])
    else:
        raise web.HTTPBadRequest

def logout(session):
    """Logs out a user"""
    _set_user(session, None)

def get_user(session, *, strip_id = False) -> dict:
    """Gets the current user for the session"""
    if "user" not in session:
        _set_user(session, None)
    user = session["user"].copy()
    if strip_id:
        user.pop("id")
    return user

@db.handle
def _set_user(cur, session, user_id: int):
    """Sets the current user for the session"""
    user = cur.execute(
        "SELECT UserID, Username FROM User WHERE UserID = ?",
        (user_id,)
    ).fetchone()

    session["user"] = {
        "username": None if user is None else user[1],
        "id": None if user is None else user[0]
    }