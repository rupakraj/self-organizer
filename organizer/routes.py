from flask import Blueprint, render_template, redirect, request, session, url_for

from organizer import db
from organizer.auth import check_pin, login_required

bp = Blueprint('main', __name__)


@bp.context_processor
def inject_globals():
    return {
        'modes':        db.get_modes(),
        'current_user': db.get_active_user(),
    }


# Auth

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if check_pin(request.form.get('pin', '')):
            session['authenticated'] = True
            return redirect(url_for('main.overview'))
        error = 'Invalid PIN.'
    return render_template('pages/login.html', error=error)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# App routes

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.overview'))


@bp.route('/overview')
@login_required
def overview():
    return render_template('pages/overview.html')


@bp.route('/<mode>/')
@login_required
def mode_overview(mode):
    modes = db.get_modes()
    mode_obj = next((m for m in modes if m['slug'] == mode), None)
    if mode_obj is None:
        return redirect(url_for('main.overview'))
    return render_template('pages/mode_overview.html', mode=mode, mode_obj=mode_obj)
