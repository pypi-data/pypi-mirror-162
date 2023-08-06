# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gemapi']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0', 'pyOpenSSL>=22.0.0,<23.0.0']

setup_kwargs = {
    'name': 'gemapi',
    'version': '0.1.0',
    'description': 'Gemapi is a lightweight Gemini framework.',
    'long_description': '# GemAPI\n\n[Gemini](https://gemini.circumlunar.space/docs/specification.html) framework written in Python.\n',
    'author': 'Thomas Sileo',
    'author_email': 't@a4.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.sr.ht/~tsileo/gemapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
