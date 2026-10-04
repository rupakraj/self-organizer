import threading

from flask import Flask

from web.api import api_bp
from web.routes import bp


def create_app():
    app = Flask(__name__)
    app.secret_key = 'change-me-in-production'
    app.register_blueprint(bp)
    app.register_blueprint(api_bp)
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

