# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinxcontrib', 'sphinxcontrib.specs']

package_data = \
{'': ['*'], 'sphinxcontrib.specs': ['theme/*', 'theme/static/*']}

install_requires = \
['Sphinx>=5.0.2,<6.0.0']

setup_kwargs = {
    'name': 'sphinxcontrib-specs',
    'version': '1.0.1',
    'description': 'Extensions for building Specializations content.',
    'long_description': None,
    'author': 'Ashley Trinh',
    'author_email': 'ashley@hackbrightacademy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
