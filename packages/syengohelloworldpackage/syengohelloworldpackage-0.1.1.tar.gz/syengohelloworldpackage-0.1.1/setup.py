# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['syengohelloworldpackage']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'syengohelloworldpackage',
    'version': '0.1.1',
    'description': 'This is a simple python package conatining a hello_world function to test skills in python package publishing.',
    'long_description': '# Syengo Hello World Package\n\n## Description\n\nThis is a simple python package conatining a hello_world function to test skills in python package publishing.\n\n### Instructions\n\n1.\n\n```cmd\npip install syengohelloworldpackage\n```\n\n2. Import hello_world from Package\n3. run func by providing an optional name= parameter\n\n### License\n\nMIT\n',
    'author': 'David Syengo',
    'author_email': 'david.syengo019@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
