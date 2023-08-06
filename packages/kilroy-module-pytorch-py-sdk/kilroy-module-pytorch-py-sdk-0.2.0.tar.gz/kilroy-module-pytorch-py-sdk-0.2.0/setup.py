# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kilroy_module_pytorch_py_sdk', 'kilroy_module_pytorch_py_sdk.resources']

package_data = \
{'': ['*']}

install_requires = \
['diskcache>=5,<6', 'torch>=1,<2']

extras_require = \
{'dev': ['pytest>=7.0,<8.0'], 'test': ['pytest>=7.0,<8.0']}

setup_kwargs = {
    'name': 'kilroy-module-pytorch-py-sdk',
    'version': '0.2.0',
    'description': 'SDK for kilroy modules using PyTorch 🧰',
    'long_description': '<h1 align="center">kilroy-module-pytorch-py-sdk</h1>\n\n<div align="center">\n\nSDK for kilroy modules using PyTorch 🧰\n\n[![Tests](https://github.com/kilroybot/kilroy-module-pytorch-py-sdk/actions/workflows/test-multiplatform.yml/badge.svg)](https://github.com/kilroybot/kilroy-module-pytorch-py-sdk/actions/workflows/test-multiplatform.yml)\n[![Docs](https://github.com/kilroybot/kilroy-module-pytorch-py-sdk/actions/workflows/docs.yml/badge.svg)](https://github.com/kilroybot/kilroy-module-pytorch-py-sdk/actions/workflows/docs.yml)\n\n</div>\n\n---\n\n## Installing\n\nUsing `pip`:\n\n```sh\npip install kilroy-module-pytorch-py-sdk\n```\n',
    'author': 'kilroy',
    'author_email': 'kilroymail@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kilroybot/kilroy-module-pytorch-py-sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
