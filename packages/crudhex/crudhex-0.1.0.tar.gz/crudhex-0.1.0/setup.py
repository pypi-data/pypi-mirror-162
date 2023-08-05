# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crudhex',
 'crudhex.adapters',
 'crudhex.adapters.application',
 'crudhex.adapters.application.cli',
 'crudhex.adapters.infrastructure',
 'crudhex.adapters.infrastructure.loader',
 'crudhex.adapters.infrastructure.template_writer',
 'crudhex.adapters.infrastructure.template_writer.config',
 'crudhex.domain',
 'crudhex.domain.config',
 'crudhex.domain.models',
 'crudhex.domain.services',
 'crudhex.domain.utils']

package_data = \
{'': ['*'],
 'crudhex.adapters.infrastructure.template_writer': ['templates/db/*',
                                                     'templates/db/fragments/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'PyYAML>=6.0,<7.0', 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['crudhex = crudhex.adapters.application.cli.main:main']}

setup_kwargs = {
    'name': 'crudhex',
    'version': '0.1.0',
    'description': 'Java/Spring CRUD code generator',
    'long_description': '# Crudhex',
    'author': 'salpreh',
    'author_email': 'salpreh.7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/salpreh/crudhex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
