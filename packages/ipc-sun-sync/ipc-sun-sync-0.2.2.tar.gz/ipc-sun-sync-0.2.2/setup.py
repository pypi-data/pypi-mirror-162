# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipc_sun_sync']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'astral>=2.2,<3.0',
 'pytimeparse>=1.1.8,<2.0.0',
 'pytz==2022.1',
 'requests>=2.28.0,<3.0.0']

entry_points = \
{'console_scripts': ['ipc-sun-sync = ipc_sun_sync.main:main']}

setup_kwargs = {
    'name': 'ipc-sun-sync',
    'version': '0.2.2',
    'description': 'Sync sunrise and sunset on Dahua IP cameras.',
    'long_description': "# ipc-sun-sync\n\n[![PyPI - License](https://img.shields.io/pypi/l/ipc-sun-sync)](./LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/ipc-sun-sync)](https://pypi.org/project/ipc-sun-sync/)\n\nSync sunrise and sunset on Dahua IP cameras.\n\n## Usage\n\nSee [config.yml.def](./config.yml.def) for a starter configuration.\n\n### Example\n\nCreate `config.yml` with the following content.\n\n```yml\n---\nlatitude: 34.0522\nlongitude: -118.2437\ntimezone: America/Los_Angeles\n\n# IP camera defaults\nusername: admin\npassword: password\nmethod: cgi\nsunrise_offset: 00:30:00\nsunset_offset: -01:20:00\n\n# IP camera list\nipc:\n  - ip: 192.168.1.108\n  - ip: 192.168.1.109\n    sunset_offset: 00:20:00\n    method: rpc\n  - ip: 192.168.1.110\n    name: FriendlyNameForLogging\n    username: OverideDefaultUser\n    password: OverideDefaultPassword123\n    channel: 1\n```\n\nThe following command will sync the cameras located at `192.168.1.108`, `192.168.1.109`, `192.168.1.110`.\n\n```\nipc-sun-sync -c config.yml\n```\n\nSunrise will be 30 minutes late and sunset will be 1 hour and 20 minutes early.\n\n`192.168.1.108` and `192.168.1.109` will use the credentials `admin` and `password`.\n\n`192.168.1.109` will interact through rpc instead of cgi and sunset will be 20 minutes late.\n\n`192.168.1.110` will have it's `name`, `username`, `password`, and `channel` overridden.\n`name` is used for logging. `channel` is the video channel you want to apply the sun times, default is 0.\n\nThe sunrise and sunset times will be calculated using the `latitude` and `longitude` variables, then it will be converted to your timezone using the `timezone` variable.\n\n### Check Configuration\n\n```\nipc-sun-sync -c config.yml --check\n```\n\n### Verify IPC Settings\n\nShows the sunrise time, sunset time, and switch mode currently on the IP cameras.\n\n```\nipc-sun-sync -c config.yml --verify\n```\n\n### Show Timezones\n\n```\nipc-sun-sync -T\n```\n\n### Show Version\n\n```\nipc-sun-sync -V\n```\n\n## Changelog\n\n[CHANGELOG.md](./CHANGELOG.md)\n\n## Troubleshooting\n\n- If the program says it is successful but the sunrise and sunset times do not change, ~~try disabling `Smart Codec` if it is enabled.~~ use rpc.\n\n## To Do\n\n- Add verbose logging.\n",
    'author': 'ItsNotGoodName',
    'author_email': 'gurnaindeol@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0.0',
}


setup(**setup_kwargs)
