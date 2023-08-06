# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt_dynamic_models']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'typer>=0.6.1,<0.7.0']

extras_require = \
{'bigquery': ['dbt-bigquery>=1.0.0,<2.0.0'],
 'databricks': ['dbt-databricks>=1.0.0,<2.0.0'],
 'postgres': ['dbt-postgres>=1.0.0,<2.0.0'],
 'redshift': ['dbt-redshift>=1.0.0,<2.0.0'],
 'snowflake': ['dbt-snowflake>=1.0.0,<2.0.0'],
 'spark': ['dbt-spark>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['dbtgen = dbt_dynamic_models.cli:main']}

setup_kwargs = {
    'name': 'dbt-dynamic-models',
    'version': '0.1.1',
    'description': 'Generate dbt models from config',
    'long_description': None,
    'author': 'Doug Guthrie',
    'author_email': 'douglas.p.guthrie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
