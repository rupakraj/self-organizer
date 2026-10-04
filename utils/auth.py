from werkzeug.security import check_password_hash

from utils import db


def check_pin(pin):
    user = db.get_active_user()
    if user is None:
        return False
    return check_password_hash(user['pin_hash'], pin)
