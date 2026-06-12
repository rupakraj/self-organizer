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
        db.executemany(
            'INSERT OR IGNORE INTO modes (slug, name) VALUES (?, ?)',
            _SEED_MODES,
        )


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
