# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['djutil']

package_data = \
{'': ['*']}

install_requires = \
['Django-Autocomplete-Light>=3.9.4,<4.0.0',
 'Django-Model-Utils>=4.2.0,<5.0.0',
 'Django>=4.1,<5.0']

setup_kwargs = {
    'name': 'dj-util',
    'version': '0.0.0.dev1',
    'description': 'Django Utilities',
    'long_description': '# Django Utilities\n',
    'author': 'The Vinh LUONG (LƯƠNG Thế Vinh)',
    'author_email': 'TheVinhLuong@gmail.com',
    'maintainer': 'The Vinh LUONG (LƯƠNG Thế Vinh)',
    'maintainer_email': 'TheVinhLuong@gmail.com',
    'url': 'https://GitHub.com/Django-AI/Dj-Util',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
