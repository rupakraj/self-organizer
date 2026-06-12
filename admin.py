import argparse
import getpass

from werkzeug.security import generate_password_hash

from organizer import db


def cmd_create_user():
    db.init_db()
    username = input('Username: ').strip()
    if not username:
        print('Error: username cannot be empty.')
        return
    pin = getpass.getpass('PIN: ').strip()
    if not pin.isdigit():
        print('Error: PIN must be numeric.')
        return
    db.create_user(username, generate_password_hash(pin))
    print(f"User '{username}' created and set as active.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create_user', action='store_true', help='Create or replace the active user')
    args = parser.parse_args()

    if args.create_user:
        cmd_create_user()
    else:
        parser.print_help()
