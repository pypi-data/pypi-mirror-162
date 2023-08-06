# AA Inactivity

This is a player activity monitoring plugin app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) (AA).

![release](https://img.shields.io/pypi/v/aa-inactivity?label=release)
![License](https://img.shields.io/badge/license-GPL-green)
![python](https://img.shields.io/pypi/pyversions/aa-inactivity)
![django](https://img.shields.io/pypi/djversions/aa-inactivity?label=django)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)


## Features

- Notify users inactive for a specified time.
- Notify administrators when users meet an inactivity theshold.
- Keep track of leave of absence requests.
- Notify administrators when leave of absence requests are created or approved.

# Installation

## Requirements

This app needs [Member Audit](https://gitlab.com/ErikKalkoken/aa-memberaudit) (and optionally, but ideally, [DiscordBot](https://github.com/pvyParts/allianceauth-discordbot)) to function. Please make sure they are installed before continuing.

## Steps

### Step 1 - Install the Package

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

`pip install aa-inactivity`

### Step 2 - Config

Add `inactivity` to your `INSTALLED_APPS`, and add the following task definition:

```python
CELERYBEAT_SCHEDULE['inactivity_check_inactivity'] = {
    'task': 'inactivity.tasks.check_inactivity',
    'schedule': crontab(minute=0, hour=0),
}
```

### Step 3 - Finalize App Installation

Run migrations:

```bash
python manage.py migrate
python manage.py collectstatic
```

Restart your supervisor services for Auth
