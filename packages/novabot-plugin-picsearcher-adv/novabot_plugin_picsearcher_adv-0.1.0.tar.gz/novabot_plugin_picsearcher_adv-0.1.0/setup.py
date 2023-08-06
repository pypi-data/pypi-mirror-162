# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['novabot_plugin_picsearcher_adv']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'lxml>=4.9.1,<5.0.0',
 'picimagesearch>=3.3.11,<4.0.0']

setup_kwargs = {
    'name': 'novabot-plugin-picsearcher-adv',
    'version': '0.1.0',
    'description': 'Nova-Bot plugin help you to find the source of (Anime) Images.',
    'long_description': None,
    'author': 'NovaNo1r',
    'author_email': 'mail@novanoir.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
