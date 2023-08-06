# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mac_cleanup']

package_data = \
{'': ['*']}

install_requires = \
['inquirer>=2.10.0,<3.0.0', 'rich>=12.2.0,<13.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['mac-cleanup = mac_cleanup.cli:main']}

setup_kwargs = {
    'name': 'mac-cleanup',
    'version': '2.2.1',
    'description': 'Python cleanup script for macOS',
    'long_description': "# mac-cleanup-py\n\n### 👨\u200d💻 Python cleanup script for macOS \n\n#### [mac-cleanup-sh](https://github.com/mac-cleanup/mac-cleanup-sh) rewritten in Python\n\n\n### What does script do?\n\n1. Cleans Trash\n2. Deletes unnecessary logs & files\n3. Removes cache\n\n![mac-cleanup_v2_2_0](https://user-images.githubusercontent.com/44712637/183507992-03466528-ddb1-4370-852c-9ef8dc008a11.gif)\n\n<details>\n   <summary>\n   Full functionality\n   </summary>\n\n  * Empty the Trash on All Mounted Volumes and the Main HDD\n  * Clear System Log Files\n  * Clear Adobe Cache Files\n  * Cleanup iOS Applications\n  * Remove iOS Device Backups\n  * Cleanup Xcode Derived Data and Archives\n  * Reset iOS simulators\n  * Cleanup Homebrew Cache\n  * Cleanup Any Old Versions of Gems\n  * Cleanup Dangling Docker Images\n  * Purge Inactive Memory\n  * Cleanup pip cache\n  * Cleanup Pyenv-VirtualEnv Cache\n  * Cleanup npm Cache\n  * Cleanup Yarn Cache\n  * Cleanup Docker Images and Stopped Containers\n  * Cleanup CocoaPods Cache Files\n  * Cleanup composer cache\n  * Cleanup Dropbox cache\n  * Remove PhpStorm logs\n  * Remove Minecraft logs and cache\n  * Remove Steam logs and cache\n  * Remove Lunar Client logs and cache\n  * Remove Microsoft Teams logs and cache\n  * Remove Wget logs and hosts\n  * Removes Cacher logs\n  * Deletes Android caches\n  * Clears Gradle caches\n  * Deletes Kite logs\n  * Clears Go module cache\n  * Clears Poetry cache\n\n</details>\n\n\n\n## Install Automatically\n\n### Using homebrew\n\n```bash\nbrew tap mac-cleanup/mac-cleanup-py\nbrew install mac-cleanup-py\n```\n\n### Using pip\n\n```bash\npip3 install rich toml inquirer \npip3 install mac-cleanup\n```\n\n## Uninstall\n\n### Using homebrew\n\n```bash\nbrew uninstall mac-cleanup-py\nbrew untap mac-cleanup/mac-cleanup-py\n```\n\n### Using pip\n\n```bash\npip3 uninstall rich toml inquirer \npip3 uninstall mac-cleanup\n```\n\n## Usage Options\n\nHelp menu:\n\n```\n$ mac-cleanup -h\n\nusage: mac-cleanup [-h] [-d] [-u] [-c] [-m]\n\n    A Mac Cleanup Utility in Python\n    v2.2.0\n    https://github.com/mac-cleanup/mac-cleanup-py\n\noptional arguments:\n  -h, --help       show this help message and exit\n  -d, --dry-run    Shows approx space to be cleaned\n  -u, --update     Script will update brew while cleaning\n  -c, --configure  Launch modules configuration\n  -m, --modules    Specify custom modules' path\n```\n",
    'author': 'Drugsosos',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mac-cleanup/mac-cleanup-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.12',
}


setup(**setup_kwargs)
