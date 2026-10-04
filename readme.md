# Self Organizer

__highly experimental__


Objective of the project is to develop the personal dashboard for self organization

__Features__
- Dashboard to put and organize the various dynamic and static sections
- Create and maintain the notes
- Tag based note categorization
- ToDo management
- ToDo Notification via SMS / Telegram / Slack etc.
- Tag based personal finance manager


__Structure__
- `utils/` shared code (database, PIN check)
- `web/` Flask web app
- `tui/` Textual terminal dashboard
- `admin.py` user management

__Setup__
```
pip install -r requirements.txt
python admin.py --create_user
```

__Run__
```
python run.py web    # browser (add --native for a desktop window, --debug, --host, --port)
python run.py tui    # terminal dashboard
```
