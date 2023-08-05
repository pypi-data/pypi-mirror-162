# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sugarloaf_utilities', 'sugarloaf_utilities.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'kubernetes>=24.2.0,<25.0.0']

entry_points = \
{'console_scripts': ['create-infrastructure = '
                     'sugarloaf_utilities.template:main',
                     'infra-utilities = sugarloaf_utilities.main:main',
                     'link-templates = '
                     'sugarloaf_utilities.template:link_templates']}

setup_kwargs = {
    'name': 'sugarloaf-utilities',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Pierce Freeman',
    'author_email': 'pierce@freeman.vc',
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
