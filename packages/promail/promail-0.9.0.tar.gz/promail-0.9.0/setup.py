# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['promail',
 'promail.clients',
 'promail.core',
 'promail.core.attachments',
 'promail.core.messages',
 'promail.filters']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=13.15.1,<14.0.0',
 'IMAPClient>=2.3.1,<3.0.0',
 'boto3-stubs>=1.24.46,<2.0.0',
 'boto3>=1.24.46,<2.0.0',
 'docformatter>=1.4,<2.0',
 'email-validator>=1.2.1,<2.0.0',
 'google-api-core>=2.8.0,<3.0.0',
 'google-api-python-client>=2.47.0,<3.0.0',
 'google-auth-httplib2>=0.1.0,<0.2.0',
 'google-auth-oauthlib>=0.5.1,<0.6.0',
 'google-auth>=2.6.6,<3.0.0',
 'nox>=2022.1.7,<2023.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pyment>=0.3.3,<0.4.0',
 'python-dotenv>=0.1.0,<0.2.0',
 'requests>=2.27.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.11.3,<5.0.0']}

setup_kwargs = {
    'name': 'promail',
    'version': '0.9.0',
    'description': 'Promail: The Python Email Automation Framework',
    'long_description': '[![Tests](https://github.com/trafire/promail/workflows/Tests/badge.svg)](https://github.com/trafire/promail/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/trafire/promail/branch/main/graph/badge.svg)](https://codecov.io/gh/trafire/promail)\n[![PyPI](https://img.shields.io/pypi/v/promail.svg)](https://pypi.org/project/promail/)\n[![Read the Docs](https://readthedocs.org/projects/promail/badge/)](https://promail.readthedocs.io/)\n# Promail\n\nPromail along with its sister library Promail-Templates aims \nto close the email gap between what you as an individual can make your\nemail do with little effort and what enterprise users do\n\n- Automated Professional Rich content HTML emails\n- Allow you to write your own pluggins that do arbitrary things depending on the content of the email.\n\n## Installation\n```\npip install promail\n```\n## Simple Usage\n\n```python\nfrom promail.clients.gmail import GmailClient\n\nclient = GmailClient("your-gmail@gmail.com")\n# The first time you do this it will open a web browser allowing you to sign into your google account directly\nclient.send_email()\n\n```\n',
    'author': 'Antoine Wood',
    'author_email': 'antoinewood@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/trafire/promail',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
