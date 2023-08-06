# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ces_mwaa_utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==5.4.1',
 'apache-airflow-providers-slack==4.1.0',
 'apache-airflow==2.2.2',
 'boto3==1.18.65',
 'requests==2.26.0']

entry_points = \
{'console_scripts': ['airflow-utils = ces_mwaa_utils.cli:run']}

setup_kwargs = {
    'name': 'ces-mwaa-utils',
    'version': '0.1.0',
    'description': 'Utilities for working for Managed Workflows for Apache Airflow',
    'long_description': None,
    'author': 'Manoj Karthick',
    'author_email': 'manojkarthick@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
