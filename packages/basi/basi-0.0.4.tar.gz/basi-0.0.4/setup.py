# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basi', 'basi._common']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.6,<5.0.0',
 'attrs>=21.4.0,<22.0.0',
 'blinker>=1.4,<2.0',
 'celery>=5.2.7,<6.0.0',
 'redis>=4.3.4,<5.0.0',
 'typing-extensions>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'basi',
    'version': '0.0.4',
    'description': 'Distributed tasks and signals',
    'long_description': '# Basi\n\n\n[![PyPi version][pypi-image]][pypi-link]\n[![Supported Python versions][pyversions-image]][pyversions-link]\n[![Build status][ci-image]][ci-link]\n[![Coverage status][codecov-image]][codecov-link]\n\n\n\n\n## Install\n\nInstall from [PyPi](https://pypi.org/project/basi/)\n\n```\npip install basi\n```\n\n## Links\n\n- __[Documentation][docs-link]__\n- __[API Reference][api-docs-link]__\n- __[Get Started][install-link]__\n- __[Contributing][contributing-link]__\n\n\n\n[docs-link]: https://davidkyalo.github.io/basi/\n[api-docs-link]: https://davidkyalo.github.io/basi/\n[install-link]: https://davidkyalo.github.io/basi/install.html\n[contributing-link]: https://davidkyalo.github.io/basi/contributing.html\n[pypi-image]: https://img.shields.io/pypi/v/basi.svg?color=%233d85c6\n[pypi-link]: https://pypi.python.org/pypi/basi\n[pyversions-image]: https://img.shields.io/pypi/pyversions/basi.svg\n[pyversions-link]: https://pypi.python.org/pypi/basi\n[ci-image]: https://github.com/davidkyalo/basi/actions/workflows/workflow.yaml/badge.svg?event=push&branch=master\n[ci-link]: https://github.com/davidkyalo/basi/actions?query=workflow%3ACI%2FCD+event%3Apush+branch%3Amaster\n[codecov-image]: https://codecov.io/gh/davidkyalo/basi/branch/master/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/davidkyalo/basi\n\n\nSee this release on GitHub: [v0.0.4](https://github.com/davidkyalo/basi/releases/tag/0.0.4)\n',
    'author': 'David Kyalo',
    'author_email': 'davidmkyalo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/davidkyalo/basi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
