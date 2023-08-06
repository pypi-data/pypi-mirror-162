# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datapipe_app']

package_data = \
{'': ['*'],
 'datapipe_app': ['frontend/*',
                  'frontend/static/css/*',
                  'frontend/static/js/*',
                  'frontend/static/media/*']}

install_requires = \
['click>=7.1.2',
 'datapipe-core>=0.11.0-beta.7,<0.12',
 'fastapi>=0.75.0',
 'uvicorn[standard]>=0.17.0']

entry_points = \
{'console_scripts': ['datapipe = datapipe_app.cli:cli']}

setup_kwargs = {
    'name': 'datapipe-app',
    'version': '0.1.6',
    'description': '',
    'long_description': '# datapipe-app\n\n`datapipe-app` implements two aspects to make every datapipe pipeline to work as\nan application:\n\n1. REST API + debug UI based of FastAPI\n1. `datapipe` CLI tool\n\n## Common usage\n\nCommon pattern to use `datapipe-app` is to create `app.py` with the following code:\n\n```\nfrom datapipe_app import DatapipeApp\n\nfrom pipeline import ds, catalog, pipeline\n\napp = DatapipeApp(ds, catalog, pipeline)\n```\n\nWhere `pipeline` is a module that defines common elements: `ds`, `catalog` and\n`pipeline`.\n\n## REST API + UI\n\n`DatapipeApp` inherits from `FastApi` app and can be started with server like\n`uvicorn`.\n\n```\nuvicorn app:app\n```\n\n### UI\n\n![Datapipe App UI](docs/datapipe-example-app.png)\n\n### REST API\n\nAPI documentation can be found at `/api/v1alpha1/docs` sub URL.\n\n## CLI\n\n`datapipe` CLI tool implements useful operations.\n\n### run\n\n`datapipe run --pipeline app`\n\nDoes full run of a specific pipeline.\n\n### table list\n\n`datapipe table list`\n\nLists all tables in pipeline.\n\n### table reset-metadata\n\n`datapipe table reset-metadata TABLE`\n\nResets metadata for a specific table: sets `updated_ts`, `processed_ts`, `hash`\nto `0`.\n',
    'author': 'Andrey Tatarinov',
    'author_email': 'a@tatarinov.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
