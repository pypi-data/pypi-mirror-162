# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory', 'understory.editor', 'understory.editor.templates']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0.0,<0.1']

entry_points = \
{'understory': ['editor = understory.editor:app']}

setup_kwargs = {
    'name': 'understory-editor',
    'version': '0.0.130',
    'description': 'Edit posts in the understory',
    'long_description': None,
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
