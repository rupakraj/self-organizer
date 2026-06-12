from flask import Blueprint, render_template, redirect, url_for

from organizer import db

bp = Blueprint('main', __name__)


@bp.context_processor
def inject_modes():
    return {'modes': db.get_modes()}


@bp.route('/')
def index():
    return redirect(url_for('main.overview'))


@bp.route('/overview')
def overview():
    return render_template('pages/overview.html')


@bp.route('/<mode>/')
def mode_overview(mode):
    modes = db.get_modes()
    mode_obj = next((m for m in modes if m['slug'] == mode), None)
    if mode_obj is None:
        return redirect(url_for('main.overview'))
    return render_template('pages/mode_overview.html', mode=mode, mode_obj=mode_obj)
