# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kittycad',
 'kittycad.api',
 'kittycad.api.api-calls',
 'kittycad.api.api-tokens',
 'kittycad.api.apps',
 'kittycad.api.beta',
 'kittycad.api.constant',
 'kittycad.api.file',
 'kittycad.api.hidden',
 'kittycad.api.meta',
 'kittycad.api.oauth2',
 'kittycad.api.payments',
 'kittycad.api.sessions',
 'kittycad.api.unit',
 'kittycad.api.users',
 'kittycad.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<23.0.0',
 'httpx>=0.15.4,<0.24.0',
 'python-dateutil>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'kittycad',
    'version': '0.3.1',
    'description': 'A client library for accessing KittyCAD',
    'long_description': '![image](https://user-images.githubusercontent.com/19377312/165883233-3bdbc9fb-ddf9-4173-8cf2-d1b70ab7127d.png)\n\n# kittycad.py\n\nThe Python API client for KittyCAD.\n\n- [PyPI](https://pypi.org/project/kittycad/)\n- [Python docs](https://python.api.docs.kittycad.io/)\n- [KittyCAD API Docs](https://docs.kittycad.io/?lang=python)\n\n## Generating\n\nYou can trigger a build with the GitHub action to generate the client. This will\nautomatically update the client to the latest version based on the spec hosted\nat [api.kittycad.io](https://api.kittycad.io/).\n\nAlternatively, if you wish to generate the client locally, make sure you have\n[Docker installed](https://docs.docker.com/get-docker/) and run:\n\n```bash\n$ make generate\n```\n\n## Contributing\n\nPlease do not change the code directly since it is generated. PRs that change\nthe code directly will be automatically closed by a bot.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
