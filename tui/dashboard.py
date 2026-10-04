import os

from rich.text import Text
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import ContentSwitcher, DataTable, Input, OptionList, Static

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


COMMANDS = ['change-category', 'reload', 'lock', 'quit']


class CategoryPicker(ModalScreen):
    BINDINGS = [('escape', 'dismiss(None)')]

    def __init__(self, names):
        super().__init__()
        self.names = names

    def compose(self):
        yield OptionList(*self.names, id='category-list')

    def on_mount(self):
        self.query_one(OptionList).border_title = 'Change category'

    def on_option_list_option_selected(self, event):
        self.dismiss(event.option_index)


class DashboardScreen(Screen):
    BINDINGS = [
        ('colon', 'open_command', 'Command'),
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
        yield Static(id='breadcrumb')
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
        yield Static(id='completions')
        yield Static(id='modeline')
        with Horizontal(id='command-row'):
            yield Input(id='command', placeholder='Press : for commands')
            yield Static(id='command-category')

    def on_mount(self):
        self.query_one('#entries', DataTable).add_columns('Name', 'Category', 'Date', 'Created')
        self.query_one('#detail-pane').border_title = 'Details'
        self.active_user = db.get_active_user()
        self.show_page(*self.current_page)

    def action_open_command(self):
        command = self.query_one('#command', Input)
        command.value = ':'
        command.focus()
        # Input resets the cursor on focus, so move it past the colon afterwards
        command.call_after_refresh(command.action_end)

    def close_command(self):
        self.query_one('#command', Input).value = ''
        self.query_one('#completions', Static).display = False
        self.query_one('#entries', DataTable).focus()

    def candidates(self, value):
        name, space, arg = value.lstrip(':').partition(' ')
        if not space:
            return [f':{c}' for c in COMMANDS if c.startswith(name.lower())]
        if name == 'change-category':
            return [f':{name} {n}' for _, n in self.pages if n.lower().startswith(arg.lower())]
        return []

    def on_input_changed(self, event):
        # Deleting the leading colon leaves command mode, like vim
        if not event.value.startswith(':'):
            if event.input.has_focus:
                self.close_command()
            return
        completions = self.query_one('#completions', Static)
        # Show only the word being completed, as Emacs does in *Completions*
        words = [c.rsplit(' ', 1)[-1].lstrip(':') for c in self.candidates(event.value)]
        completions.update(Text('   '.join(words)))
        completions.display = bool(words)

    def on_key(self, event):
        command = self.query_one('#command', Input)
        if not command.has_focus:
            return
        if event.key == 'escape':
            self.close_command()
        elif event.key == 'tab':
            # Complete up to the longest common prefix of the candidates
            found = self.candidates(command.value)
            if found:
                command.value = found[0][:len(os.path.commonprefix([c.lower() for c in found]))]
                command.action_end()
        else:
            return
        event.stop()
        event.prevent_default()

    def on_input_submitted(self, event):
        name, _, arg = event.value.lstrip(':').strip().partition(' ')
        self.close_command()
        if name == 'change-category':
            self.change_category(arg.strip())
        elif name == 'reload':
            self.action_reload()
        elif name == 'lock':
            self.app.action_lock()
        elif name in ('q', 'quit'):
            self.app.exit()
        elif name:
            self.notify(f'Unknown command: {name}', severity='error')

    def change_category(self, wanted):
        names = [name for _, name in self.pages]
        if not wanted:
            self.app.push_screen(CategoryPicker(names), self.select_category)
            return
        matches = [i for i, name in enumerate(names) if name.lower() == wanted.lower()]
        if matches:
            self.select_category(matches[0])
        else:
            self.notify(f'No category: {wanted}', severity='error')

    def select_category(self, index):
        if index is not None:
            self.show_page(*self.pages[index])

    def on_data_table_row_highlighted(self, event):
        entry, tags = db.get_entry(int(event.row_key.value))
        if entry:
            self.query_one('#detail', Static).update(entry_detail(entry, tags))

    def action_reload(self):
        self.show_page(*self.current_page)

    def show_page(self, slug, name):
        self.current_page = (slug, name)
        self.query_one('#breadcrumb', Static).update(f'Organizer/{name}')
        self.query_one('#command-category', Static).update(name)
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
        self.update_modeline('Overview', entry_label(total))
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
        self.update_modeline(name, entry_label(len(entries)))
        self.query_one('#switcher', ContentSwitcher).current = 'mode-view'

    def update_modeline(self, name, count):
        username = self.active_user['username'] if self.active_user else '-'
        self.query_one('#modeline', Static).update(Text(f' -:---  Organizer  {name}  ({count})  [{username}]'))
