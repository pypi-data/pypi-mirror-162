# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['when']

package_data = \
{'': ['*'], 'when': ['data/*']}

install_requires = \
['airportsdata>=20220406,<20220407',
 'arrow>=1.2.2,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'rich-click>=1.3.0,<2.0.0',
 'rich>=12.2.0,<13.0.0',
 'typer>=0.4.1,<0.5.0',
 'tzdata>=2022.1,<2023.0',
 'tzlocal>=4.2,<5.0']

entry_points = \
{'console_scripts': ['when-cli = when.__main__:run']}

setup_kwargs = {
    'name': 'when-cli',
    'version': '1.1.2',
    'description': 'When CLI is a timezone conversion tool. It takes as input a natural time string, can also be a time range, and converts it into different timezone(s) at specific location(s).',
    'long_description': '\n<p align="center">\n  <img\n    width="400"\n    src="https://raw.githubusercontent.com/chassing/when-cli/master/media/logo.jpg"\n    alt="When CLI"\n  />\n</p>\n\n[![PyPI version][pypi-version]][pypi-link]\n[![PyPI platforms][pypi-platforms]][pypi-link]\n[![Black][black-badge]][black-link]\n![PyPI - License](https://img.shields.io/pypi/l/when-cli)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/chassing/when-cli/Test?label=tests)\n![GitHub Release Date](https://img.shields.io/github/release-date/chassing/when-cli)\n\n# When CLI\n\n<img\n  src="https://raw.githubusercontent.com/chassing/when-cli/master/media/example.png"\n  alt="Example"\n  width="50%"\n  align="right"\n/>\n\n**when-cli** is a timezone conversion tool. It takes as input a natural time string, can also be a time range, and converts it into different timezone(s) at specific location(s).\n\n- **Local:** Everything runs on your local machine, no internet connection needed\n- **Fast:** it\'s fast! 🚀\n- **Easy:** quick to install – start using it in minutes.\n- **Customizable:** configure every aspect to your needs.\n- **Colorful:** beautiful colors and Emoji 😎 support.\n\n## Installation\n\nYou can install **when-cli** from [PyPI](https://pypi.org/project/when-cli/) with `pipx`):\n\n```bash\n$ pipx install when-cli\n```\n\nor install it with `pip`:\n```bash\n$ python3 -m pip install when-cli\n```\n\nYou can also download and use the pre-build binary from the latest [Release](https://github.com/chassing/when-cli/releases).\n\n\n## Usage\n\n```bash\n$ when-cli "7. May 06:00 to May 7th 12:00 in PMI" -l America/Los_Angeles -l klu -l PMI\n```\n<img\n  src="https://raw.githubusercontent.com/chassing/when-cli/master/media/example.png"\n  alt="Example"\n/>\n\nSee [Usage](https://github.com/chassing/when-cli/blob/master/USAGE.md) for more details.\n\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)\n\n## Logo\n\n[vecteezy.com](https://www.vecteezy.com/vector-art/633173-clock-icon-symbol-sign)\n\n\n\n[black-badge]:              https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]:               https://github.com/psf/black\n[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github\n[github-discussions-link]:  https://github.com/chassing/when-cli/discussions\n[pypi-link]:                https://pypi.org/project/when-cli/\n[pypi-platforms]:           https://img.shields.io/pypi/pyversions/when-cli\n[pypi-version]:             https://badge.fury.io/py/when-cli.svg\n',
    'author': 'Christian Assing',
    'author_email': 'chris@ca-net.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chassing/when-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
