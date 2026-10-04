from textual.app import App

from tui.dashboard import DashboardScreen
from tui.login import LoginScreen
from utils.auth import check_pin


class OrganizerApp(App):
    TITLE = 'Self Organizer'
    CSS_PATH = 'app.tcss'

    def __init__(self, dev_pin=None):
        super().__init__()
        self.dev_pin = dev_pin

    def on_mount(self):
        if self.dev_pin and check_pin(self.dev_pin):
            self.push_screen(DashboardScreen())
        else:
            self.push_screen(LoginScreen())

    # Screen transitions live here so the screens don't import each other
    def unlock(self):
        self.switch_screen(DashboardScreen())

    def action_lock(self):
        self.switch_screen(LoginScreen())
