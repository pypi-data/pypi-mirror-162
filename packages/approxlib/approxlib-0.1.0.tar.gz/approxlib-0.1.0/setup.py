# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['approx',
 'approx.core',
 'approx.core.backend',
 'approx.core.device',
 'approx.core.quant']

package_data = \
{'': ['*']}

install_requires = \
['numpy==1.21', 'torch>=1.12,<2.0', 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'approxlib',
    'version': '0.1.0',
    'description': "Too lazy to quantize? Don't worry! Just tell approx to cast everything automatically!",
    'long_description': '# `approx`\n\nQuantization made easy\n',
    'author': 'sudomaze',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/approx-ml/approx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.13,<4.0.0',
}


setup(**setup_kwargs)
