# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ceg']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['ceg = ceg.cli:ceg_cli']}

setup_kwargs = {
    'name': 'ceg',
    'version': '0.2.0',
    'description': 'A simple gist crud utility.',
    'long_description': "See `Project's Readme <https://www.github.com/justaus3r/ceg/blob/Master/README.rst>`_ for info\n",
    'author': 'Justaus3r',
    'author_email': 'x-neron@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/justaus3r/ceg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
