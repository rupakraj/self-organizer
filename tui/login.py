from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Static

from utils import db
from utils.auth import check_pin


class LoginScreen(Screen):
    def compose(self):
        active_user = db.get_active_user()
        yield Header()
        with Vertical(id='login-box'):
            if active_user is None:
                yield Label('No user found. Create one with:')
                yield Label('python admin.py --create_user', classes='hint')
            else:
                yield Label(f"Welcome back, {active_user['username']}", markup=False)
                yield Input(placeholder='PIN', password=True, id='pin')
                yield Static(id='login-error')
        yield Footer()

    def on_input_submitted(self, event):
        if check_pin(event.value):
            self.app.unlock()
        else:
            event.input.value = ''
            self.query_one('#login-error', Static).update('Invalid PIN.')
