# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kubiya']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.79.0,<0.80.0', 'uvicorn>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'kubiya',
    'version': '0.0.4',
    'description': 'kubiya.ai has a ',
    'long_description': None,
    'author': 'Kubiya',
    'author_email': 'info@kubiya.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.7.2,<3.11',
}


setup(**setup_kwargs)
