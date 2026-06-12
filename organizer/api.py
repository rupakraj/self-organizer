import re

from flask import Blueprint, jsonify, request

from organizer import db
from organizer.auth import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def _tag_data(data):
    name = (data.get('name') or '').strip()
    if not name:
        return None, 'Name is required.'
    return {
        'name':  name,
        'slug':  (data.get('slug') or _slugify(name)).strip(),
        'color': data.get('color') or '#6366f1',
        'icon':  (data.get('icon') or '').strip(),
    }, None


# Tags

@api_bp.get('/tags')
@login_required
def list_tags():
    return jsonify([dict(t) for t in db.get_tags()])


@api_bp.post('/tags')
@login_required
def create_tag():
    fields, err = _tag_data(request.get_json(silent=True) or {})
    if err:
        return jsonify({'error': err}), 400
    try:
        db.create_tag(**fields)
        return jsonify({'ok': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.put('/tags/<int:tag_id>')
@login_required
def update_tag(tag_id):
    fields, err = _tag_data(request.get_json(silent=True) or {})
    if err:
        return jsonify({'error': err}), 400
    db.update_tag(tag_id, **fields)
    return jsonify({'ok': True})


@api_bp.delete('/tags/<int:tag_id>')
@login_required
def delete_tag(tag_id):
    db.set_tag_active(tag_id, 0)
    return jsonify({'ok': True})


@api_bp.post('/tags/<int:tag_id>/restore')
@login_required
def restore_tag(tag_id):
    db.set_tag_active(tag_id, 1)
    return jsonify({'ok': True})
