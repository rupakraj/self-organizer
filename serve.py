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


def run_web(host, port, debug=False):
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def run_native(host, port, debug=False):
    import webview

    app = create_app()
    server = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=debug),
        daemon=True,
    )
    server.start()

    webview.create_window('Self Organizer', f'http://{HOST}:{PORT}')
    webview.start()


if __name__ == '__main__':
    db.init_db()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--web',    action='store_true', help='Run in browser (default)')
    group.add_argument('--native', action='store_true', help='Run as native desktop window')
    parser.add_argument('--debug',  default=True, help='Enable debug mode')
    parser.add_argument('--host',   default=HOST, help='Host to bind the server to')
    parser.add_argument('--port',   default=PORT, type=int, help='Port to bind the server to')
    args = parser.parse_args()

    debug = args.debug
    host = args.host
    port = args.port

    if args.native:
        run_native(host, port, debug)
    else:
        run_web(host, port, debug)
