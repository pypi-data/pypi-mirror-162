# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydrogen_lambda', 'hydrogen_lambda.aws', 'hydrogen_lambda.datadog']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'hydrogen-lambda',
    'version': '0.1.0',
    'description': 'Get the message content from an input event',
    'long_description': None,
    'author': 'nael.vindolet',
    'author_email': 'nael.vindolet@sewan.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
