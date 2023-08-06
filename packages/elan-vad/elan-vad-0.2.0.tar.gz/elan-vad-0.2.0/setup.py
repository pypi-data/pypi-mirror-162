# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elan_vad']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0',
 'pympi-ling>=1.70.2,<2.0.0',
 'torch>=1.12.0,<2.0.0',
 'torchaudio>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['cluster = elan_vad.cli:cluster',
                     'vad = elan_vad.cli:vad']}

setup_kwargs = {
    'name': 'elan-vad',
    'version': '0.2.0',
    'description': 'A utility library to perform Voice Audio Detection on .wav files, write these sections to an elan file, and optionally cluster annotations on a given tier based on the VAD sections.',
    'long_description': '# Elan-vad \nElan vad is a tool to perform Voice Activity Detection related tasks on Elan files\n\n## Installation\nYou can install the package with `pip install elan-vad` (or `pip3` on macs).\n\nAfter installation, you can import the utilities into your python program with:\n```python\nfrom elan_vad import *\n```\n\nThe package additionally comes with two CLI programs: `vad` and `cluster`, which\ncan be used to perform the utilities from the terminal. \n\n## Usage\n### As a Library\nThe example below: \n  - Performs VAD on an audio file, \n  - Adds these detected sections to an elan file (under the tier "\\_vad"),\n  - And then clusters the annotations within an existing tier ("Phrase") to be \n    constrained within the VAD sections.\n\n```python\nfrom pathlib import Path\nfrom pympi.Elan import Eaf\nfrom elan_vad import detect_voice, add_vad_tier, cluster_tier_by_vad\n\n# Replace these paths with the correct values for your application\nsound_file: Path = \'audio.wav\'\nelan_file: Path = \'test.eaf\'\n\n# Open up the Elan file for modification.\nelan = Eaf(elan_file)\n\n# Perform VAD on the sound_file\nspeech = detect_voice(sound_file)\nadd_vad_tier(elan, speech, \'_vad\')\n\n# Cluster annotations within a \'Phrase\' tier by the VAD sections\ncluster_tier_by_vad(elan, \'Phrase\', \'_vad\', \'vad_cluster\')\n\n# Replace the elan file with the new data\nelan.to_file(elan_file)\n```\n\n### From the terminal\ntodo \n',
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
