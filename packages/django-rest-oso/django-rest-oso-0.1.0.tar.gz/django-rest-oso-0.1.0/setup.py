# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_rest_oso']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0,<5', 'django-oso>=0.26,<0.27', 'djangorestframework>=3.13,<4']

setup_kwargs = {
    'name': 'django-rest-oso',
    'version': '0.1.0',
    'description': 'Oso implementation for Django Rest.',
    'long_description': 'Django Rest implementation of Django Oso.\n',
    'author': 'Javier Alonso Shannon',
    'author_email': 'javier.as@medicalwebexperts.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
