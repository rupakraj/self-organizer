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
