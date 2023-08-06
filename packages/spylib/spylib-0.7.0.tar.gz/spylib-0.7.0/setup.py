# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spylib', 'spylib.oauth', 'spylib.utils', 'spylib.webhook']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'httpx>=0.18.1',
 'nest-asyncio>=1.5.1,<2.0.0',
 'pycryptodome>=3.10.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'starlette>=0.15.0',
 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'spylib',
    'version': '0.7.0',
    'description': "A library to facilitate interfacing with Shopify's API",
    'long_description': '# Shopify Python Library - SPyLib\n\nThe Shopify python library, or SPyLib, simplifies the use of the Shopify\nservices such as the REST and GraphQL APIs as well as the OAuth authentication.\nAll of this is done **asynchronously using asyncio**.\n\n![Tests](https://github.com/SatelCreative/satel-spylib/actions/workflows/tests.yml/badge.svg)\n\n## Installation\n\n```bash\npip install spylib\n```\n\n## What can SPyLib do?\n\n[Official documentation](https://satelcreative.github.io/spylib)\n\nShopify components managed by SPyLib:\n\n* Admin API\n* Install an app through OAuth\n* Session tokens\n* Webhooks\n* Multipass\n',
    'author': 'Anthony Hillairet',
    'author_email': 'ant@satel.ca',
    'maintainer': 'Anthony Hillairet',
    'maintainer_email': 'ant@satel.ca',
    'url': 'https://satelcreative.github.io/spylib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
