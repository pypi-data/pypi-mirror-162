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
 'crudhex.adapters.infrastructure.template_writer.services',
 'crudhex.domain',
 'crudhex.domain.config',
 'crudhex.domain.models',
 'crudhex.domain.services',
 'crudhex.domain.services.db',
 'crudhex.domain.services.domain',
 'crudhex.domain.utils']

package_data = \
{'': ['*'],
 'crudhex.adapters.infrastructure.template_writer': ['templates/db/*',
                                                     'templates/db/fragments/*',
                                                     'templates/domain/*',
                                                     'templates/domain/fragments/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'PyYAML>=6.0,<7.0', 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['crudhex = crudhex.adapters.application.cli.main:main']}

setup_kwargs = {
    'name': 'crudhex',
    'version': '0.5.0',
    'description': 'Java/Spring CRUD code generator',
    'long_description': "# Crudhex\n\n[![PyPI version](https://badge.fury.io/py/crudhex.svg)](https://badge.fury.io/py/crudhex)\n\n⚠️ **Warn: Alpha development stage**\n\n---\n\nCLI tool to generate Java CRUD classes from a spec file. The target for this code generation is a Hexagonal architecture.\n\n\n## Motivation\nAdding CRUD operation in a hexagonal project is quite a pain. You can take shortcuts that can be totally legit in cases of just CRUD operations, but most cases if there is already a rich domain/application layer for other use cases CRUD shortcuts can break the consistency of the project.\n\nThe target of this CLI is to ease ~~my life~~ and try to give a general solution to CRUD generations in Hexagonal architecture. There are some customizations you can make, but some aspects for now are closed to customization for now.\n\n## Getting started\n\n### Project config file\nProject config file is used to know where things should go in the project. Usually contains a path to the sources folder (`src/main/java` in regular maven projects) and packages where things are located within that source folder.\nHere is a basic example:\n```yaml\nsrc: src/main/java # Java source folder for single module apps (where your packages start)\n\ndomain-models-pkg: com.salpreh.baseapi.domain.models # domain models package\ndb-models-pkg: com.salpreh.baseapi.adapers.infrasturcture.db.models # db entities package\nrest-models-pkg: com.salpreh.baseapi.adapters.api.models # rest api models\n```\n\nIn case of multi-module project you will have to specify `src` path to each module (domain, rest adapter and db adapter). More examples of config can be found in (`doc/examples/config`).\n\nThe default name for this config file is `.crudhex-conf.yaml`, located in the root of the project (you can provide the path to config file by cli options, so you can place it anywhere you want)\n\n### Spec file\nThis is the file where you specify the crud model. Class name, attributes and some meta data about DB structure (relations, PK field, column name alias, etc).\n\nAn example of spec file:\n```yaml\nPerson: # Model name\n  .meta:\n    table-name: persons # OPTIONAL: Table name for entity\n  id: # Field name\n    type: Long\n    id: sequence # PK marker. This field will be the primary key for the entity. \n                 # As value you specify generation strategy available in JPA with lower case.\n  birthPlanet: # Field name\n    type: Planet\n    column: birth_planet # OPTIONAL: Column name alias\n    relation: # OPTIONAL: DB relation meta data\n      type: many-to-one # Relation type\n      join-column: birth_planet_id # Join column for relation\n  affiliations:\n    type: Faction\n    relation:\n      type: many-to-many # In case of many-to-many we have a couple of more meta about DB setup\n      join-table: person_affiliation \n      join-column: person_id\n      inverse-join-column: faction_id\n  backup:\n    type: Person\n    relation:\n      type: one-to-one\n      join-column: backup_id\n  backing:\n    type: Person\n    relation:\n      type: one-to-one\n      mapped-by: backup # Mapping attribute for non-owning side of relation\n```\n\nSnippet config comments provide a overview of each relevant section in config. I'll dig further in config details in a dedicated section.\nFor now, you can find some aditional examples in `doc/examples/spec`.\n\n### Installation\n\nPackage is published in Pypi public repositories. You can use [pip]() (or another convinient python dependency manager) to install the package:\n```shell\npip install crudhex\n```\n\nOnce installed you should be able to use it as CLI tool:\n```shell\ncrudhex --help\n```",
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
