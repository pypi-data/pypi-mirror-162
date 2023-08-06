# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gtn_tools', 'gtn_tools.exceptions', 'gtn_tools.quote']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'ShopifyAPI>=10.0.0,<11.0.0',
 'XlsxWriter>=3.0.1,<4.0.0',
 'attrs>=21.2.0,<22.0.0',
 'google-cloud-speech>=2.10.0,<3.0.0',
 'google-cloud-storage>=1.42.3,<2.0.0',
 'google-cloud-translate>=3.5.0,<4.0.0',
 'imutils>=0.5.4,<0.6.0',
 'iniconfig>=1.1.1,<2.0.0',
 'langdetect>=1.0.9,<2.0.0',
 'lxml>=4.6.3,<5.0.0',
 'numpy>=1.21.2,<2.0.0',
 'opencv-python>=4.5.3,<5.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'pluggy>=1.0.0,<2.0.0',
 'py>=1.10.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pydub>=0.25.1,<0.26.0',
 'pyparsing>=2.4.7,<3.0.0',
 'python-docx>=0.8.11,<0.9.0',
 'python-pptx>=0.6.21,<0.7.0',
 'six>=1.16.0,<2.0.0',
 'srt>=3.5.0,<4.0.0',
 'starlette>=0.16.0,<0.17.0',
 'tesserocr>=2.5.2,<3.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'gtn-tools',
    'version': '1.6.0',
    'description': 'Common tools and utils for GeTraNet APIs and internal services.',
    'long_description': None,
    'author': 'GeTraNet',
    'author_email': 'dev@getranet.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
