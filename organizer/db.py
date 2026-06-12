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
        db.executemany(
            'INSERT OR IGNORE INTO modes (slug, name) VALUES (?, ?)',
            _SEED_MODES,
        )


def get_modes():
    with _connect() as db:
        return db.execute('SELECT slug, name FROM modes ORDER BY id').fetchall()
