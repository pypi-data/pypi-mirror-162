# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kilroy_module_huggingface', 'kilroy_module_huggingface.resources']

package_data = \
{'': ['*']}

install_requires = \
['deepmerge>=1.0,<2.0',
 'kilroy-module-pytorch-py-sdk>=0.2,<0.3',
 'kilroy-module-server-py-sdk>=0.6,<0.7',
 'transformers>=4.21,<5.0',
 'typer[all]>=0.4,<0.5']

extras_require = \
{'dev': ['pytest>=7.0,<8.0'], 'test': ['pytest>=7.0,<8.0']}

entry_points = \
{'console_scripts': ['kilroy-module-huggingface = '
                     'kilroy_module_huggingface.__main__:cli']}

setup_kwargs = {
    'name': 'kilroy-module-huggingface',
    'version': '0.2.0',
    'description': 'kilroy module using Hugging Face models 🤗',
    'long_description': '<h1 align="center">kilroy-module-huggingface</h1>\n\n<div align="center">\n\nkilroy module using Hugging Face models 🤗\n\n[![Multiplatform tests](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/test-multiplatform.yml/badge.svg)](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/test-multiplatform.yml)\n[![Docker tests](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/test-docker.yml/badge.svg)](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/test-docker.yml)\n[![Docs](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/docs.yml/badge.svg)](https://github.com/kilroybot/kilroy-module-huggingface/actions/workflows/docs.yml)\n\n</div>\n\n---\n\n## Installing\n\nUsing `pip`:\n\n```sh\npip install kilroy-module-huggingface\n```\n',
    'author': 'kilroy',
    'author_email': 'kilroymail@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kilroybot/kilroy-module-huggingface',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
