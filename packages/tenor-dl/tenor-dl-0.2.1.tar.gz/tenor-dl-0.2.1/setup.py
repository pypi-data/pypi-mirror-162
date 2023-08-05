# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tenor_dl']

package_data = \
{'': ['*']}

install_requires = \
['pyquery>=1.4.3,<2.0.0', 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['tenor-dl = tenor_dl.tenor_dl:main']}

setup_kwargs = {
    'name': 'tenor-dl',
    'version': '0.2.1',
    'description': 'simple CLI script to easily download gifs from tenor.com',
    'long_description': '# tenor-dl\n\nSimple CLI script to download gifs from tenor.com.\n\n## Installation\n\n```bash\npip3 install tenor-dl\n```\n\n## Usage\n\n```bash\nusage: tenor-dl [-h] [-o OUTPUT] [-u] URL\n\nsimple script to download gifs from tenor.com\n\npositional arguments:\n  URL                   tenor.com URL to download the gif from\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTPUT, --output OUTPUT\n                        output path or use "-" for STDOUT\n  -u, --urlonly         only print direct link to gif and exit\n```\n\n## Example Usage\n\n```bash\ntenor-dl https://tenor.com/view/rage-work-pc-stressed-pissed-gif-15071896\n```\n',
    'author': 'zocker-160',
    'author_email': 'zocker1600@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
