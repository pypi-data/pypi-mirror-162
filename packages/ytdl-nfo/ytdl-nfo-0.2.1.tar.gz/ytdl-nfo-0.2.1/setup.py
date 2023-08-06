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
    'version': '0.2.1',
    'description': 'Utility to convert youtube-dl/yt-dlp json metadata to .nfo',
    'long_description': '# ytdl-nfo : youtube-dl NFO generator\n\n[youtube-dl](https://github.com/ytdl-org/youtube-dl) is an incredibly useful resource to download and archive footage from across the web. Viewing and organising these files however can be a bit of a hassle.\n\n**ytdl-nfo** takes the `--write-info-json` output from youtube-dl and parses it into Kodi-compatible .nfo files. The aim is to prepare and move files so as to be easily imported into media centers such as Plex, Emby, Jellyfin, etc. \n\n**Warning**\nThis package is still in early stages and breaking changes may be introduced.\n\n## Installation\nRequirements: Python 3.6\n### Python 3 pipx (recommended)\n[pipx](https://github.com/pipxproject/pipx) is tool that installs a package and its dependiencies in an isolated environment. This is useful to not affect existing packages or installs. Visit their [github page](https://github.com/pipxproject/pipx) to learn more and for installation instructions.\n\n1. Ensure Python 3.6 and [pipx](https://github.com/pipxproject/pipx) is installed\n2. Run the following command to install with pipx\n``` bash\npipx install git+https://github.com/owdevel/ytdl_nfo.git\n```\n\n### Python 3 pip\n1. Ensure Python 3.6 is installed\n2. Run the following command to install with pip\n```bash\npip install git+https://github.com/owdevel/ytdl_nfo.git\n```\n\n### Package from source\n1. Ensure Python 3.6 is installed\n2. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`\n3. Cd into the directory\n4. Install requirements using pip `pip install -r requirements.txt`\n5. Install the package with `pip install .`\n\n#### Run without packaging (dev)\n1. Perform steps 1-4 of package from source\n2. Ensure the current working directory is set to the cloned folder\n3. Run with `python -m ytdl_nfo`\n\n\n## Usage\n### Automatic\nRun `ytdl-nfo JSON_FILE` replacing `JSON_FILE` with either the path to the file you wish to convert, or a folder containing files to convert. The tool will automatically take any files ending with `.json` and convert them to `.nfo` using the included extractor templates.\n\n#### Examples\nConvert a single file\n```bash\nytdl-nfo great_video.info.json\n```\n\nConvert a directory and all sub directories with `.info.json` files\n```bash\nytdl-nfo video_folder\n```\n\n### Manual\nytdl-nfo uses a set of YAML configs to determine the output format and what data comes across. This is dependent on the extractor flag which is set by youtube-dl. Should this fail to be set or if a custom extractor is wanted there is the `--extractor` flag. ytdl-nfo will then use extractor with the given name as long as it is in the config directory with the format `custom_extractor_name.yaml`.\n\n```bash\nytdl-nfo --extractor custom_extractor_name great_video.info.json\n```\n\n#### Config Location\nRun the following command to get the configuration location.\n```bash\nytdl-nfo --config\n```\n\n## Extractors\nIssues/Pull Requests are welcome to add more youtube-dl supported extractors to the repo.\n\n### Custom Extractors\nComing Soon...\n\n## Todo\n- [ ] Add try catches to pretty print errors\n- [ ] Recursive folder searching\n- [ ] Documentation and templates for creating custom extractors\n- [ ] Add package to pypi\n\n## Authors Note\nThis is a small project I started to learn how to use python packaging system whilst providing some useful functionality for my home server setup. Feel free to contact me at owdevel@gmail.com with any feedback, suggestions or criticisms. Hope you have a great day :).\n',
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
