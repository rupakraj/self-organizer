import argparse
import sys
from pathlib import Path

from utils import db

ENV_PATH = Path(__file__).parent / '.env'


def read_env():
    if not ENV_PATH.exists():
        return {}
    pairs = (line.split('=', 1) for line in ENV_PATH.read_text().splitlines() if '=' in line and not line.lstrip().startswith('#'))
    return {key.strip(): value.strip().strip('"\'') for key, value in pairs}


def run_web(args):
    from web.app import run_native, run_web

    if args.native:
        run_native(args.host, args.port)
    else:
        run_web(args.host, args.port, args.debug)


def run_tui(args):
    from tui.app import OrganizerApp

    dev_pin = None
    if args.dev:
        dev_pin = read_env().get('DEV_PIN')
        if not dev_pin:
            sys.exit(f'--dev needs DEV_PIN set in {ENV_PATH}')
    OrganizerApp(dev_pin).run()


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
    tui.add_argument('--dev', action='store_true', help='Skip login using DEV_PIN from .env')
    tui.set_defaults(run=run_tui)

    args = parser.parse_args()
    db.init_db()
    args.run(args)
