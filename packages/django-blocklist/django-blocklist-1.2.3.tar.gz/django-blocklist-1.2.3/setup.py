# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_blocklist',
 'django_blocklist.management',
 'django_blocklist.management.commands',
 'django_blocklist.migrations',
 'django_blocklist.tests']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2,<5']

setup_kwargs = {
    'name': 'django-blocklist',
    'version': '1.2.3',
    'description': 'A Django app that implements IP-based blocklisting.',
    'long_description': '# Django-blocklist\nThis is a [Django][] app that implements IP-based blocklisting. Its `BlocklistMiddleware` performs the blocking, and its `clean_blocklist` management command deletes entries which have satisfied the cooldown period. Entries also have a `reason` field, used in reporting. There are utility functions to add/remove IPs, an admin, and several management commands.\n\nThis app is primarily for situations where server-level blocking is not available, e.g. on platform-as-a-service hosts like PythonAnywhere or Heroku. Being an application-layer solution, it\'s not as performant as blocking via firewall or web server process, but is suitable for moderate traffic sites. It also offers better integration with the application stack, for easier management.\n\n## Quick start\n1. The [PyPI package name is `django-blocklist`](https://pypi.org/project/django-blocklist/); add that to your `requirements.txt` or otherwise install it into your project\'s Python environment.\n\n0. Add "django_blocklist" to your INSTALLED_APPS setting like this:\n\n        INSTALLED_APPS = [\n        ...\n        "django_blocklist"\n        ]\n\n0. Add the middleware like this:\n\n       MIDDLEWARE = [\n           ...\n          "django_blocklist.middleware.BlocklistMiddleware"\n       ]\n\n0. Run `python manage.py migrate` to create the `django_blocklist_blockedip` table.\n0. Add IPs to the list (via management commands,  `utils.add_to_blocklist`, or the admin).\n0. Set up a `cron` job or equivalent to run `manage.py clean_blocklist` daily.\n\n## Management commands\nDjango-blocklist includes several management commands:\n\n* `add_to_blocklist` &mdash; (one or more IPs)\n* `remove_from_blocklist` &mdash; (one or more IPs)\n* `search_blocklist` &mdash; look for an IP in the list; in addition to info on stdout, returns an exit code of 0 if successful\n* `update_blocklist` &mdash; change the `reason` or `cooldown` values for existing entries\n* `import_blocklist` &mdash; convenience command for importing IPs from a file\n* `report_blocklist` &mdash; information on the current entries\n* `clean_blocklist` &mdash; remove entries that have fulfilled their cooldown period\n\nThe `--help` for each of these details its available options.\n\nFor exporting or importing BlockedIP entries, use Django\'s built-in `dumpdata` and `loaddata` management commands.\n\n## Configuration\nYou can customize the following settings via a `BLOCKLIST_CONFIG` dict in your project settings:\n* `cooldown` &mdash; Days to expire, for new entries; default 7\n* `cache-ttl` &mdash; Seconds that utils functions cache the full list; default 60\n* `denial-template` &mdash; For the denial response; an f-string with `{ip}` and `{cooldown}` placeholders\n\n## Reporting\nThe `report_blocklist` command gives summary information about the current collection of IPs, including how many requests from those IPs have been blocked. See the [sample report](blocklist-report-sample-obfuscated.txt) for more.\n\n## Utility methods\nThe `utils` module defines two convenience functions for updating the list from your application code:\n* `add_to_blocklist(ips: set, reason="")` adds IPs to the blocklist\n* `remove_from_blocklist(ip: str)` removes an entry, returning `True` if successful\n\n[django]: https://www.djangoproject.com/',
    'author': 'Paul Bissex',
    'author_email': 'paul@bissex.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/paul_bissex/django-blocklist',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
