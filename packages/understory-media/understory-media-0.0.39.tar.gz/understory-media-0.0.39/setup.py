# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory', 'understory.media', 'understory.media.templates']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0.0,<0.1']

entry_points = \
{'understory': ['media = understory.media:app']}

setup_kwargs = {
    'name': 'understory-media',
    'version': '0.0.39',
    'description': 'Manage media in the understory',
    'long_description': '# understory-media\nManage media in the understory\n',
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
