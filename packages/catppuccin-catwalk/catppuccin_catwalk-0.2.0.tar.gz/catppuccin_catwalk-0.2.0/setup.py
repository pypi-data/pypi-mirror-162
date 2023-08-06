# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['catwalk']

package_data = \
{'': ['*']}

extras_require = \
{':platform_machine != "x86_64"': ['Pillow>=9.2.0,<10.0.0'],
 ':platform_machine == "x86_64"': ['Pillow-SIMD>=9.0.0,<10.0.0']}

entry_points = \
{'console_scripts': ['catwalk = catwalk:cli']}

setup_kwargs = {
    'name': 'catppuccin-catwalk',
    'version': '0.2.0',
    'description': 'Part of catppuccin/toolbox, to generate preview a single composite screenshot for the four flavours',
    'long_description': None,
    'author': 'Catppuccin Org',
    'author_email': 'core@catppuccin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/catppuccin/toolbox',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
