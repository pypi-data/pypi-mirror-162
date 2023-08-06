# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_pgschemas',
 'django_pgschemas.contrib',
 'django_pgschemas.contrib.channels2',
 'django_pgschemas.contrib.channels3',
 'django_pgschemas.contrib.files',
 'django_pgschemas.management',
 'django_pgschemas.management.commands',
 'django_pgschemas.postgresql_backend',
 'django_pgschemas.test']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.1,<4.2', 'psycopg2>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'django-pgschemas',
    'version': '0.10.0',
    'description': 'Multi-tenancy on Django using PostgreSQL schemas.',
    'long_description': 'django-pgschemas\n================\n\n.. image:: https://img.shields.io/badge/packaging-poetry-purple.svg\n    :alt: Packaging: poetry\n    :target: https://github.com/sdispater/poetry\n\n.. image:: https://img.shields.io/badge/code%20style-black-black.svg\n    :alt: Code style: black\n    :target: https://github.com/ambv/black\n\n.. image:: https://github.com/lorinkoz/django-pgschemas/workflows/code/badge.svg\n    :alt: Build status\n    :target: https://github.com/lorinkoz/django-pgschemas/actions\n\n.. image:: https://readthedocs.org/projects/django-pgschemas/badge/?version=latest\n    :alt: Documentation status\n    :target: https://django-pgschemas.readthedocs.io/\n\n.. image:: https://coveralls.io/repos/github/lorinkoz/django-pgschemas/badge.svg?branch=master\n    :alt: Code coverage\n    :target: https://coveralls.io/github/lorinkoz/django-pgschemas?branch=master\n\n.. image:: https://badge.fury.io/py/django-pgschemas.svg\n    :alt: PyPi version\n    :target: http://badge.fury.io/py/django-pgschemas\n\n.. image:: https://pepy.tech/badge/django-pgschemas/month\n    :alt: Downloads\n    :target: https://pepy.tech/project/django-pgschemas/\n\n|\n\nThis app uses PostgreSQL schemas to support data multi-tenancy in a single\nDjango project. It is a fork of `django-tenants`_ with some conceptual changes:\n\n- There are static tenants and dynamic tenants. Static tenants can have their\n  own apps and urlconf.\n- Tenants can be simultaneously routed via subdomain and via subfolder on shared\n  subdomain.\n- Public is no longer the schema for storing the main site data. Public should\n  be used only for true shared data across all tenants. Table "overriding" via\n  search path is no longer encouraged.\n- Management commands can be run on multiple schemas via wildcards - the\n  multiproc behavior of migrations was extended to just any tenant command.\n\n.. _django-tenants: https://github.com/tomturner/django-tenants\n\nWhich package to use?\n---------------------\n\nThere are currently multiple packages to handle multi-tenancy via PostgreSQL schemas.\nThis table should help you make an informed decision on which one to choose.\n\n.. list-table::\n   :widths: 50 50\n   :header-rows: 1\n\n   * - Package\n     - Features\n   * - `django-tenant-schemas`_\n     - Original project.\n       Active and maintained by `@goodtune`_.\n   * - `django-tenants`_\n     - Active and maintained by `@tomturner`_.\n       Built on top of `django-tenant-schemas`_.\n       Uses a ``Domain`` model for allowing multiple domains per tenant.\n       Allows for parallel migrations with custom migration executor.\n       Other multiple improvements.\n   * - `django-pgschemas`_\n     - Active and maintained by `@lorinkoz`_.\n       Built on top of `django-tenants`_.\n       Different philosphy for tenants.\n       Other improvements listed above.\n\n.. _django-tenants-schemas: https://github.com/bernardopires/django-tenant-schemas\n.. _@goodtune: https://github.com/goodtune\n.. _django-tenants: https://github.com/tomturner/django-tenants\n.. _@tomturner: https://github.com/tomturner\n.. _django-pgschemas: https://github.com/lorinkoz/django-pgschemas\n.. _@lorinkoz: https://github.com/lorinkoz\n\nDocumentation\n-------------\n\nhttps://django-pgschemas.readthedocs.io/\n\nBreaking changes\n----------------\n\nv0.9.0\n++++++\n\n- Dropped support for Python < 3.8, Django < 3.1.\n\nv0.7.0\n++++++\n\n- Changed public API for getting/setting active schema. Public API is now\n  ``get_current_schema``, ``activate(schema)``, ``activate_public()``. Any\n  schema descriptor can still be used as context manager.\n- Changed location of tenant model and domain model in settings.\n  ``TENANT_MODEL`` and ``DOMAIN_MODEL`` keys are now under ``TENANTS["default"]``\n  instead of ``TENANTS["public"]``. This is required for future\n  static-tenant-only configurations.\n- Module ``cache`` renamed to ``contrib.cache``.\n- Module ``contrib.channels`` renamed to ``contrib.channels2``.\n- Added module ``contrib.channels3``.\n- Management command option ``--executor {sequential, parallel}`` renamed to\n  ``--parallel``.\n- All signals renamed. Added ``schema_activate`` signal.\n\nContributing\n------------\n\n- Join the discussion at https://github.com/lorinkoz/django-pgschemas/discussions.\n- PRs are welcome! If you have questions or comments, please use the link\n  above.\n- To run the test suite run ``make`` or ``make coverage``. The tests for this\n  project live inside a small django project called ``dpgs_sandbox``. Database\n  password and database host can be set through the environment variables\n  ``DATABASE_PASSWORD`` and ``DATABASE_HOST``.\n\nCredits\n-------\n\n* Tom Turner for `django-tenants`_\n* Bernardo Pires for `django-tenant-schemas`_\n\n.. _django-tenants: https://github.com/tomturner/django-tenants\n.. _django-tenant-schemas: https://github.com/bernardopires/django-tenant-schemas\n',
    'author': 'Lorenzo Peña',
    'author_email': 'lorinkoz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lorinkoz/django-pgschemas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
