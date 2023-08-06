# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['think_dashboard_agent', 'think_dashboard_agent.providers']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler>=3.9.1,<4.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'redis>=4.3.4,<5.0.0',
 'requests>=2.28.1,<3.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'think-dashboard-agent',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Suhrob Malikov',
    'author_email': 'suhrob@thinkland.uz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
