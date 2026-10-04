from rich.text import Text
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import ContentSwitcher, DataTable, Footer, Header, Label, ListItem, ListView, Static

from utils import db


def entry_label(n):
    return f"{n} entr{'y' if n == 1 else 'ies'}"


def category_cell(entry):
    if not entry['category_name']:
        return ''
    return Text.assemble(('● ', entry['category_color'] or ''), entry['category_name'])


def entry_detail(entry, tags):
    lines = [Text(entry['name'], 'bold')]
    meta = ' · '.join(v for v in (entry['entry_date'], entry['category_name']) if v)
    if meta:
        lines.append(Text(meta, 'dim'))
    if tags:
        lines.append(Text('  ').join(Text(f"{t['icon']} {t['name']}".strip(), t['color']) for t in tags))
    lines += [Text(''), Text(entry['description'] or 'No description.')]
    return Text('\n').join(lines)


class DashboardScreen(Screen):
    BINDINGS = [
        ('r', 'reload', 'Refresh'),
        ('l', 'app.lock', 'Lock'),
        ('q', 'app.quit', 'Quit'),
    ]

    def __init__(self):
        super().__init__()
        # A slug of None is the overview page
        self.pages = [(None, 'Overview')] + [(m['slug'], m['name']) for m in db.get_modes()]
        self.current_page = self.pages[0]

    def compose(self):
        yield Header(show_clock=True)
        with Horizontal(id='panes'):
            yield ListView(*[ListItem(Label(name)) for _, name in self.pages], id='sidebar')
            with Vertical(id='main-pane'):
                yield Static(id='page-title')
                with ContentSwitcher(initial='overview', id='switcher'):
                    with Horizontal(id='overview'):
                        for _ in self.pages[1:]:
                            yield Static(classes='card')
                    with Vertical(id='mode-view'):
                        yield DataTable(id='entries', cursor_type='row')
                        with VerticalScroll(id='detail-pane'):
                            yield Static(id='detail')
        yield Footer()

    def on_mount(self):
        self.query_one('#entries', DataTable).add_columns('Name', 'Category', 'Date', 'Created')
        self.query_one('#detail-pane').border_title = 'Details'
        active_user = db.get_active_user()
        self.sub_title = f"Welcome, {active_user['username']}" if active_user else ''
        self.show_page(*self.current_page)

    def on_list_view_highlighted(self, event):
        if event.list_view.index is not None:
            self.show_page(*self.pages[event.list_view.index])

    def on_data_table_row_highlighted(self, event):
        entry, tags = db.get_entry(int(event.row_key.value))
        if entry:
            self.query_one('#detail', Static).update(entry_detail(entry, tags))

    def action_reload(self):
        self.show_page(*self.current_page)

    def show_page(self, slug, name):
        self.current_page = (slug, name)
        if slug is None:
            self.show_overview()
        else:
            self.show_mode(slug, name)

    def show_overview(self):
        total = 0
        for card, (slug, name) in zip(self.query('.card'), self.pages[1:]):
            entry_count = len(db.get_entries(slug))
            total += entry_count
            card.border_title = name
            card.update(entry_label(entry_count))
        self.query_one('#page-title', Static).update(f'Overview · {entry_label(total)}')
        self.query_one('#switcher', ContentSwitcher).current = 'overview'

    def show_mode(self, slug, name):
        entries = db.get_entries(slug)
        entries_table = self.query_one('#entries', DataTable)
        entries_table.clear()
        for e in entries:
            entries_table.add_row(
                Text(e['name']),
                category_cell(e),
                e['entry_date'] or '',
                e['created_at'][:10],
                key=str(e['id']),
            )
        detail = entry_detail(*db.get_entry(entries[0]['id'])) if entries else 'No entries yet.'
        self.query_one('#detail', Static).update(detail)
        self.query_one('#page-title', Static).update(f'{name} · {entry_label(len(entries))}')
        self.query_one('#switcher', ContentSwitcher).current = 'mode-view'
