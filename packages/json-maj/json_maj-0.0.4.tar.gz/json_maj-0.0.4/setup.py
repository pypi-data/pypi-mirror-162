# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_maj']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['updatejson = json_maj.cli:cli']}

setup_kwargs = {
    'name': 'json-maj',
    'version': '0.0.4',
    'description': 'Updates Jsons w/ json, key pair, or entire dictionary as arguments',
    'long_description': None,
    'author': 'anthony galassi',
    'author_email': '28850131+bendhouseart@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
