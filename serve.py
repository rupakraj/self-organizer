import argparse
import threading

from flask import Flask

from organizer import db
from organizer.routes import bp

HOST = '127.0.0.1'
PORT = 5000


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


def run_web(host, port, debug):
    create_app().run(host=host, port=port, debug=debug)


def run_native(host, port):
    import webview

    server = threading.Thread(
        target=lambda: create_app().run(host=host, port=port),
        daemon=True,
    )
    server.start()

    webview.create_window('Self Organizer', f'http://{host}:{port}')
    webview.start()


if __name__ == '__main__':
    db.init_db()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--web',    action='store_true', help='Run in browser (default)')
    group.add_argument('--native', action='store_true', help='Run as native desktop window')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--host',  default=HOST,        help='Host to bind')
    parser.add_argument('--port',  default=PORT,        type=int, help='Port to bind')
    args = parser.parse_args()

    if args.native:
        run_native(args.host, args.port)
    else:
        run_web(args.host, args.port, args.debug)
