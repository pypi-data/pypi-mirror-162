# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pic_resizer']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['pic_resizer = pic_resizer.entry:main']}

setup_kwargs = {
    'name': 'pic-resizer',
    'version': '0.1.3',
    'description': 'A image resizing tool.',
    'long_description': None,
    'author': 'fffzlfk',
    'author_email': '1319933925qq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
