# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobiketrax']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'auth0-python>=3.23.1,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0']

entry_points = \
{'console_scripts': ['biketrax = aiobiketrax.cli:run']}

setup_kwargs = {
    'name': 'aiobiketrax',
    'version': '0.2.0',
    'description': 'Python library for interacting with the PowUnity BikeTrax GPS tracker.',
    'long_description': '# aiobiketrax\nPython library for interacting with the PowUnity BikeTrax GPS tracker.\n\n[![Linting](https://github.com/basilfx/aiobiketrax/actions/workflows/lint.yml/badge.svg)](https://github.com/basilfx/aiobiketrax/actions/workflows/lint.yml)\n[![PyPI version](https://badge.fury.io/py/aiobiketrax.svg)](https://badge.fury.io/py/aiobiketrax)\n\n## Introduction\nThis library is mainly written to work with a custom component for\nHome Assistant. You can find this custom component\n[here](https://github.com/basilfx/homeassistant-biketrax).\n\nThe [PowUnity BikeTrax](https://powunity.com/) is a GPS tracker for electric\nbicycles. It provides real-time updates every when the bike is in motion, using\na 2G modem. It works in Europe, and requires a subscription after a trial\nperiod of one year.\n\n### Features\n* Multi-device support.\n* Traccar and admin API support.\n* Live updates using websocket.\n\nNot implemented:\n\n* Geofencing.\n* Global configuration, such as webhooks.\n\n### Known issues\nThe [schemas](contrib/generator/schema.json) of the models haven been\nreversed-engineerd by observing responses for a small number of devices. It is\nlikely that responses of other devices do not map onto the current models. For\nexample, some properties are not set if they have never been configured from\nthe app.\n\nPlease open an issue, and provide some responses so that the schemas can be\nimproved. Be sure to redact sensitive information, such as locations, unique\nidentifiers and personal details.\n\n## Usage\n\n### In code\n```python\nfrom aiobiketrax import Account\n\nimport aiohttp\n\nasync with aiohttp.ClientSession() as session:\n    account = Account(\n        username="someone@example.org",\n        password="secret",\n        session=session)\n\n    await account.update_devices()\n\n    for device in account.devices:\n        print(device.name)\n```\n\n### CLI\nFor demonstration and testing purposes, one can use the CLI as well. If you\nhave the package installed, use `biketrax --help` command to get started.\n\n## Contributing\nSee the [`CONTRIBUTING.md`](CONTRIBUTING.md) file.\n\n## License\nSee the [`LICENSE.md`](LICENSE.md) file (MIT license).\n\n## Disclaimer\nUse this library at your own risk. I cannot be held responsible for any\ndamages.\n\nThis page and its content is not affiliated with PowUnity.',
    'author': 'Bas Stottelaar',
    'author_email': 'basstottelaar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/basilfx/aiobiketrax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
