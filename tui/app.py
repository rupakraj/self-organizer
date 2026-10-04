from textual.app import App

from tui.dashboard import DashboardScreen
from tui.login import LoginScreen


class OrganizerApp(App):
    TITLE = 'Self Organizer'
    CSS_PATH = 'app.tcss'

    def on_mount(self):
        self.push_screen(LoginScreen())

    # Screen transitions live here so the screens don't import each other
    def unlock(self):
        self.switch_screen(DashboardScreen())

    def action_lock(self):
        self.switch_screen(LoginScreen())
