# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['debug_toolbar_user_switcher']

package_data = \
{'': ['*'],
 'debug_toolbar_user_switcher': ['templates/debug_toolbar_user_switcher/*']}

install_requires = \
['django-debug-toolbar>=2,<4', 'django>=2.2,<5']

setup_kwargs = {
    'name': 'django-debug-toolbar-user-switcher',
    'version': '2.2.0',
    'description': 'Panel for the Django Debug toolbar to quickly switch between users.',
    'long_description': 'django-debug-toolbar-user-switcher\n==================================\n\nForked from https://chris-lamb.co.uk/projects/django-debug-toolbar-user-panel.\n\nUpdated for Debug Toolbar 2.x.\n',
    'author': 'Thread Engineering',
    'author_email': 'tech@thread.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thread/django-debug-toolbar-user-switcher/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
