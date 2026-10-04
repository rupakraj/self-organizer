from functools import wraps

from flask import redirect, session, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper
