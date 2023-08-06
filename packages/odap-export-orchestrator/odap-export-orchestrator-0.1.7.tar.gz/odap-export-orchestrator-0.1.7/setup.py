# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['persona_export',
 'persona_export.configuration',
 'persona_export.exports',
 'persona_export.services',
 'persona_export.sql',
 'persona_export.utils']

package_data = \
{'': ['*']}

install_requires = \
['azure.storage.blob>=12.8.1,<13.0.0',
 'pandas>=1.2.4,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'tables>=3.6.1,<4.0.0']

setup_kwargs = {
    'name': 'odap-export-orchestrator',
    'version': '0.1.7',
    'description': 'DataSentics odap export orchestrator',
    'long_description': '# ODAP EXPORT ORCHESTRATOR\n\n**This package is distributed under the "DataSentics SW packages Terms of Use." See [license](https://github.com/DataSentics/odap-export-orchestrator/blob/main/LICENSE)**\n\nThis module exports data based on config sent from Persona application backend. It’s part of the application, it exports data from featurestore, etc to inmemory dataset of application. It’s scheduled from backend of the application and also all information needed to make correct export get from backend in form of json.',
    'author': 'Pavla Moravkova',
    'author_email': 'pavla.moravkova@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DataSentics/odap-export-orchestrator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
