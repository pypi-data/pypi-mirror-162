# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vocoder', 'vocoder.acoustic_models', 'vocoder.lexicons']

package_data = \
{'': ['*']}

install_requires = \
['aioconsole>=0.5.0,<0.6.0',
 'graphviz>=0.20.1,<0.21.0',
 'lark-parser',
 'loguru',
 'numpy',
 'sounddevice',
 'torch',
 'tqdm',
 'transformers',
 'webrtcvad']

setup_kwargs = {
    'name': 'vocoder-dictation',
    'version': '0.1.0',
    'description': 'Dictation for programmers',
    'long_description': '# Vocoder\n\nVocoder is a software package for dictation and voice control. For details, see the [user guide](./docs/user-guide.md).\n',
    'author': 'ricky',
    'author_email': 'rickycontact9@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ricky0123/vocoder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
