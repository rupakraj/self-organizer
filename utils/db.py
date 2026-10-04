import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'app.db'

_SEED_MODES = [
    ('hobby',     'Hobby'),
    ('academics', 'Academics'),
    ('clients',   'Clients'),
]


def _connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with _connect() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS modes (
                id   INTEGER PRIMARY KEY,
                slug TEXT    UNIQUE NOT NULL,
                name TEXT    NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS login (
                id         INTEGER PRIMARY KEY,
                username   TEXT    NOT NULL,
                pin_hash   TEXT    NOT NULL,
                is_active  INTEGER NOT NULL DEFAULT 1,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id         INTEGER PRIMARY KEY,
                name       TEXT    NOT NULL,
                slug       TEXT    UNIQUE NOT NULL,
                color      TEXT    NOT NULL DEFAULT '#6366f1',
                icon       TEXT    NOT NULL DEFAULT '',
                is_active  INTEGER NOT NULL DEFAULT 1,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id         INTEGER PRIMARY KEY,
                name       TEXT    NOT NULL,
                slug       TEXT    UNIQUE NOT NULL,
                color      TEXT    NOT NULL DEFAULT '#6366f1',
                icon       TEXT    NOT NULL DEFAULT '',
                is_active  INTEGER NOT NULL DEFAULT 1,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id          INTEGER PRIMARY KEY,
                mode_slug   TEXT    NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                name        TEXT    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                entry_date  TEXT,
                is_active   INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER NOT NULL REFERENCES entries(id),
                tag_id   INTEGER NOT NULL REFERENCES tags(id),
                PRIMARY KEY (entry_id, tag_id)
            )
        ''')
        db.executemany(
            'INSERT OR IGNORE INTO modes (slug, name) VALUES (?, ?)',
            _SEED_MODES,
        )


# Auth

def get_modes():
    with _connect() as db:
        return db.execute('SELECT slug, name FROM modes ORDER BY id').fetchall()


def get_active_user():
    with _connect() as db:
        return db.execute(
            'SELECT * FROM login WHERE is_active = 1 ORDER BY id DESC LIMIT 1'
        ).fetchone()


def create_user(username, pin_hash):
    with _connect() as db:
        db.execute('UPDATE login SET is_active = 0')
        db.execute(
            'INSERT INTO login (username, pin_hash, is_active) VALUES (?, ?, 1)',
            (username, pin_hash),
        )


# Tags

def get_tags():
    with _connect() as db:
        return db.execute(
            'SELECT * FROM tags ORDER BY is_active DESC, name'
        ).fetchall()


def create_tag(name, slug, color, icon):
    with _connect() as db:
        db.execute(
            'INSERT INTO tags (name, slug, color, icon) VALUES (?, ?, ?, ?)',
            (name, slug, color, icon),
        )


def update_tag(tag_id, name, slug, color, icon):
    with _connect() as db:
        db.execute(
            'UPDATE tags SET name=?, slug=?, color=?, icon=? WHERE id=?',
            (name, slug, color, icon, tag_id),
        )


def set_tag_active(tag_id, is_active):
    with _connect() as db:
        db.execute('UPDATE tags SET is_active=? WHERE id=?', (is_active, tag_id))


# Categories

def get_categories():
    with _connect() as db:
        return db.execute(
            'SELECT * FROM categories ORDER BY is_active DESC, name'
        ).fetchall()


def create_category(name, slug, color, icon):
    with _connect() as db:
        db.execute(
            'INSERT INTO categories (name, slug, color, icon) VALUES (?, ?, ?, ?)',
            (name, slug, color, icon),
        )


def update_category(category_id, name, slug, color, icon):
    with _connect() as db:
        db.execute(
            'UPDATE categories SET name=?, slug=?, color=?, icon=? WHERE id=?',
            (name, slug, color, icon, category_id),
        )


def set_category_active(category_id, is_active):
    with _connect() as db:
        db.execute('UPDATE categories SET is_active=? WHERE id=?', (is_active, category_id))


# Entries

def get_entries(mode_slug):
    with _connect() as db:
        return db.execute(
            '''SELECT e.*, c.name AS category_name, c.color AS category_color
               FROM entries e
               LEFT JOIN categories c ON c.id = e.category_id
               WHERE e.mode_slug = ? AND e.is_active = 1
               ORDER BY e.created_at DESC''',
            (mode_slug,),
        ).fetchall()


def get_entry(entry_id):
    with _connect() as db:
        entry = db.execute(
            '''SELECT e.*, c.name AS category_name
               FROM entries e
               LEFT JOIN categories c ON c.id = e.category_id
               WHERE e.id = ?''',
            (entry_id,),
        ).fetchone()
        if entry is None:
            return None, []
        tags = db.execute(
            '''SELECT t.* FROM tags t
               JOIN entry_tags et ON et.tag_id = t.id
               WHERE et.entry_id = ?''',
            (entry_id,),
        ).fetchall()
        return entry, tags


def create_entry(mode_slug, name, description, entry_date, category_id, tag_ids):
    with _connect() as db:
        cur = db.execute(
            'INSERT INTO entries (mode_slug, name, description, entry_date, category_id) VALUES (?, ?, ?, ?, ?)',
            (mode_slug, name, description, entry_date or None, category_id or None),
        )
        entry_id = cur.lastrowid
        if tag_ids:
            db.executemany(
                'INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)',
                [(entry_id, tid) for tid in tag_ids],
            )
        return entry_id


def update_entry_name(entry_id, name):
    with _connect() as db:
        db.execute('UPDATE entries SET name=? WHERE id=?', (name, entry_id))


def get_entry_tag_ids(entry_id):
    with _connect() as db:
        rows = db.execute('SELECT tag_id FROM entry_tags WHERE entry_id = ?', (entry_id,)).fetchall()
        return [r['tag_id'] for r in rows]
