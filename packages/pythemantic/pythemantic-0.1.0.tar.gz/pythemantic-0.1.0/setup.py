# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythemantic']

package_data = \
{'': ['*'],
 'pythemantic': ['.git/*',
                 '.git/hooks/*',
                 '.git/info/*',
                 '.git/logs/*',
                 '.git/logs/refs/heads/*',
                 '.git/objects/0e/*',
                 '.git/objects/19/*',
                 '.git/objects/42/*',
                 '.git/objects/4d/*',
                 '.git/objects/6b/*',
                 '.git/objects/87/*',
                 '.git/objects/8a/*',
                 '.git/objects/9c/*',
                 '.git/objects/9f/*',
                 '.git/objects/ab/*',
                 '.git/objects/cf/*',
                 '.git/objects/ed/*',
                 '.git/objects/f1/*',
                 '.git/objects/f8/*',
                 '.git/refs/heads/*']}

setup_kwargs = {
    'name': 'pythemantic',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Khayelihle Tshuma',
    'author_email': 'khayelihle.tshuma@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
