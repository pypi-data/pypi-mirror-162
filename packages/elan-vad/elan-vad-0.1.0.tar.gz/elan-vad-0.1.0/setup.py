# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elan_vad']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0', 'pympi-ling>=1.70.2,<2.0.0', 'silero>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['cluster = elan_vad.cli:cluster',
                     'vad = elan_vad.cli:vad']}

setup_kwargs = {
    'name': 'elan-vad',
    'version': '0.1.0',
    'description': 'A utility library to perform Voice Audio Detection on .wav files, write these sections to an elan file, and optionally cluster annotations on a given tier based on the VAD sections.',
    'long_description': '# Elan-vad \nA good job.\n',
    'author': 'Harry Keightley',
    'author_email': 'harrykeightley@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CoEDL/elan-vad',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
