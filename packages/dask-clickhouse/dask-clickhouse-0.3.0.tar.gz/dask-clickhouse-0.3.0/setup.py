# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dask_clickhouse']

package_data = \
{'': ['*']}

install_requires = \
['dask>=2022.7.1,<2023.0.0',
 'ibis-framework[clickhouse]>=3.1.0,<4.0.0',
 'pyarrow>=9.0.0,<10.0.0']

setup_kwargs = {
    'name': 'dask-clickhouse',
    'version': '0.3.0',
    'description': 'Dask integration for Clickhouse',
    'long_description': '# Dask-Clickhouse\n\nDask Clickhouse connector.\n\n## Installation\n\n```shell\npip install dask-clickhouse\n```\n\n## Usage\n\n`dask-clickhouse` provides `read_from_table` and `write_to_table` methods for parallel IO to and from Clickhouse with Dask.\n\n```python\nfrom dask_clickhouse import read_clickhouse\n\nquery = "SELECT * FROM example_table"\n\nddf = read_clickhouse(\n    query=query,\n    connection_kwargs={"...": "..."}\n)\n```\n',
    'author': 'Michael Harris',
    'author_email': 'mharris@luabase.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mharrisb1/dask-clickhouse',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
