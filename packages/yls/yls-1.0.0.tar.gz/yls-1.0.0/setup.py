# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yls']

package_data = \
{'': ['*']}

install_requires = \
['pluggy>=1.0.0,<2.0.0', 'pygls>=0.11.3,<0.12.0', 'yaramod>=3.12.8,<4.0.0']

entry_points = \
{'console_scripts': ['yls = yls.server:main']}

setup_kwargs = {
    'name': 'yls',
    'version': '1.0.0',
    'description': 'YARA Language Server',
    'long_description': '# YLS\n[Language server](https://microsoft.github.io/language-server-protocol/) for\n[YARA](https://yara.readthedocs.io/en/stable/) language.\n\n:rocket: Features:\n- Code completion of all available modules (including function parameters)\n- Function documentation for hovers and code completion\n- Opinionated code formatting\n- Signature help\n- Linting\n- Go-to definition and references\n- Symbol highlighting under the cursor\n- Debugging? Stay tuned...\n- ...\n\n![Showcase](https://github.com/avast/yls/raw/master/assets/yls.png)\n\n:snake: Minimal supported version of Python is `3.8`.\n\n## Installation\n\nTo setup your environment please follow instructions on\n[wiki](https://github.com/avast/yls/wiki/How-to-setup).\n\n## How to develop\n\nInstall YLS in development mode with all necessary dependencies.\n\n```bash\npoetry install\n```\n\n### Tests\n\nYou can run tests with the following command:\n\n```bash\npoetry run pytest\n```\n\n### Code style\n\nYLS uses [black](https://github.com/psf/black) to format and check code. In\norder to format the code accordingly you can use prepared `poetry run poe format`.\n\n## License\n\nCopyright (c) 2022 Avast Software, licensed under the MIT license. See the\n[`LICENSE`](https://github.com/avast/yls/blob/master/LICENSE) file for more\ndetails.\n\nYLS and its related projects uses third-party libraries or other resources\nlisted, along with their licenses, in the\n[`LICENSE-THIRD-PARTY`](https://github.com/avast/yls/blob/master/LICENSE-THIRD-PARTY)\nfile.\n\n## FAQ\n\n### Why are you using `pluggy`?\n\nSome parts depend on our internal services, however we are working on making\nmost of the code available. This is just the first piece.\n',
    'author': 'Matej Kašťák',
    'author_email': 'matej.kastak@avast.com',
    'maintainer': 'Matej Kašťák',
    'maintainer_email': 'matej.kastak@avast.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
