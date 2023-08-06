# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nops_sink', 'nops_sink.tests']

package_data = \
{'': ['*']}

install_requires = \
['boto3>1.22', 'nops_kafka>0.1', 'smart_open>4.0']

setup_kwargs = {
    'name': 'nops-sink',
    'version': '0.2.0',
    'description': 'Set of modules to simplify submission of data to the various sinks.',
    'long_description': None,
    'author': 'nOps Engineers',
    'author_email': 'eng@nops.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
