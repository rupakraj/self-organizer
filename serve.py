import argparse
import threading

from flask import Flask, render_template, redirect, url_for

from organizer import db

app = Flask(__name__)

HOST = '127.0.0.1'
PORT = 5000


# ── Inject modes into every template ─────────────────────────────────────────

@app.context_processor
def inject_modes():
    return {'modes': db.get_modes()}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('overview'))


@app.route('/overview')
def overview():
    return render_template('pages/overview.html')


@app.route('/<mode>/')
def mode_overview(mode):
    modes = db.get_modes()
    mode_obj = next((m for m in modes if m['slug'] == mode), None)
    if mode_obj is None:
        return redirect(url_for('overview'))
    return render_template('pages/mode_overview.html', mode=mode, mode_obj=mode_obj)


# ── Launch modes ──────────────────────────────────────────────────────────────

def run_web():
    app.run(host=HOST, port=PORT, debug=True)


def run_native():
    import webview

    server = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORT),
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
    args = parser.parse_args()

    if args.native:
        run_native()
    else:
        run_web()
