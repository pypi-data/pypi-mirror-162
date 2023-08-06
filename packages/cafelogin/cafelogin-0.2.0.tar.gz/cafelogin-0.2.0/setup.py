# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cafelogin', 'cafelogin.portals']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.2.3,<2.0.0',
 'colorama>=0.4.4,<0.5.0',
 'selenium>=3.14.1,<4.0.0',
 'webdriver-manager>=3.8.3,<4.0.0']

entry_points = \
{'console_scripts': ['cafelogin = cafelogin:run']}

setup_kwargs = {
    'name': 'cafelogin',
    'version': '0.2.0',
    'description': 'Login to wifi portals commonly found at cafes.',
    'long_description': '# cafelogin\n\nA python command line tool for logging into cafe wifi portals.\n\n### Compatibility:\n- Browser WebDriver\n  - Chrome\n  - Firefox (Geckodriver)\n- Wifi Portal\n  - https://service.wi2.ne.jp\n    - Starbucks JP\n    - Wired Cafe JP\n    - Doutor JP\n\n## Install\n\n```zsh\npip install cafelogin\n```\n\n## Usage\n\n```sh\ncafelogin [-h] [-c CONFIG_FILE] [--version] [--browser {chrome,firefox}] [--chrome-driver-version CHROME_DRIVER_VERSION] [--firefox-driver-version FIREFOX_DRIVER_VERSION] [--watch] [--watch-interval WATCH_INTERVAL]\n```\n\nExamples:\n\n```sh\n# Check portal connection and login via any detected portal\ncafelogin\n\n# Watch the portal connection continuously for changes\ncafelogin --watch\n\n# Specify a web-driver version to use\ncafelogin --driver-version "v0.28.0"\n```\n\n## WebDriver cache\n\nRun the command once with an internet connection to install the web-driver to the cache.\n\n```\ncafelogin\n\n[WDM] - ====== WebDriver manager ======\n[WDM] - There is no [linux64] geckodriver for browser  in cache\n[WDM] - Getting latest mozilla release info for v0.29.0\n[WDM] - Trying to download new driver from https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz\n[WDM] - Driver has been saved in cache [/home/me/.wdm/drivers/geckodriver/linux64/v0.29.0]\n```\n',
    'author': 'Ben Nordstrom',
    'author_email': 'bennord@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bennord/cafelogin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
