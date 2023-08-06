# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ytdl_nfo']

package_data = \
{'': ['*'], 'ytdl_nfo': ['configs/*']}

install_requires = \
['PyYAML>=6.0,<7.0']

entry_points = \
{'console_scripts': ['ytdl-nfo = ytdl_nfo:main']}

setup_kwargs = {
    'name': 'ytdl-nfo',
    'version': '0.2.0',
    'description': 'Utility to convert youtube-dl/yt-dlp json metadata to .nfo',
    'long_description': None,
    'author': 'Owen',
    'author_email': 'owdevel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/owdevel/ytdl-nfo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
