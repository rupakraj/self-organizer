import argparse

from utils import db


def run_web(args):
    from web.app import run_native, run_web

    if args.native:
        run_native(args.host, args.port)
    else:
        run_web(args.host, args.port, args.debug)


def run_tui(args):
    from tui.app import OrganizerApp

    OrganizerApp().run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    modes = parser.add_subparsers(dest='mode', required=True)

    web = modes.add_parser('web', help='Run the web app')
    web.add_argument('--native', action='store_true', help='Run as native desktop window')
    web.add_argument('--debug',  action='store_true', help='Enable debug mode')
    web.add_argument('--host',   default='127.0.0.1', help='Host to bind')
    web.add_argument('--port',   default=5000, type=int, help='Port to bind')
    web.set_defaults(run=run_web)

    tui = modes.add_parser('tui', help='Run the terminal dashboard')
    tui.set_defaults(run=run_tui)

    args = parser.parse_args()
    db.init_db()
    args.run(args)
