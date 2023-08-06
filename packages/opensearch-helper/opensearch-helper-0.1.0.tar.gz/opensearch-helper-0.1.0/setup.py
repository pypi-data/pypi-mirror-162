# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opensearch_helper',
 'opensearch_helper.bp',
 'opensearch_helper.dmo',
 'opensearch_helper.svc']

package_data = \
{'': ['*']}

install_requires = \
['baseblock==0.1.4', 'boto3', 'opensearch-py>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'opensearch-helper',
    'version': '0.1.0',
    'description': 'OpenSearch Helper for Easy I/O',
    'long_description': None,
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
