from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash

from organizer import db


def check_pin(pin):
    user = db.get_active_user()
    if user is None:
        return False
    return check_password_hash(user['pin_hash'], pin)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper
