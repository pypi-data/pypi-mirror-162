# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tap_feed', 'tap_feed.tests', 'tap_feed.tests.parser']

package_data = \
{'': ['*']}

install_requires = \
['feedparser>=6.0.8,<7.0.0',
 'requests>=2.25.1,<3.0.0',
 'singer-sdk>=0.8.0,<0.9.0']

entry_points = \
{'console_scripts': ['tap-feed = tap_feed.tap:TapFeed.cli']}

setup_kwargs = {
    'name': 'tap-feed',
    'version': '1.1.1',
    'description': 'A Singer tap for RSS and Atom feeds built with the Meltano SDK for Singer Taps.',
    'long_description': '[![Tests](https://github.com/jawats/tap-feed/actions/workflows/tests.yml/badge.svg)](https://github.com/jawats/tap-feed/actions/workflows/tests.yml)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) \n\n# tap-feed\n\n`tap-feed` is a Singer tap for various feeds and was built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.\nThis tap can be used with RSS and Atom based feeds thanks to [feedparser](https://feedparser.readthedocs.io/en/latest/index.html).\n\n## Installation\n\nTo install this tap, simply run the following command in your terminal:\n\n```bash\npipx install tap-feed\n```\n\nOr if you don\'t want to use pipx:\n\n```bash\npip3 install tap-feed\n```\n\n## Configuration\n\n### Accepted Config Options\n\n| Property                   | Type             | Required? | Description                                                                |\n| ---                        | ---              | ---       | ---                                                                        |\n| feed_urls                  | String           | Yes       | A list of one or more feed paths                                           |\n| feed_fields                 | Array of Strings | Yes       | A list of feed level data fields to capture                                 |\n| feed_entry_fields           | Array of Strings | Yes       | A list of entry level data fields to capture                                |\n| feed_entry_replication_key | String           | Yes       | The field used to determine new records, typically \'published\' or \'updated\' |\n| start_date                 | Date Time        | No        | The earliest record date to sync                                           |\n\nA full list of supported settings and capabilities for this\ntap is available by running:\n\n```bash\ntap-feed --about\n```\n\n### Example Config File\n```json\n{\n  "feed_urls": ["http://feeds.feedburner.com/PythonSoftwareFoundationNews", "https://talkpython.fm/episodes/rss"],\n  "feed_fields": ["title", "subtitle"],\n  "feed_entry_fields": ["id", "title", "link"],\n  "feed_entry_replication_key": "published"\n}\n```\n\n## Usage\n\nYou can easily run `tap-feed` by itself or in a pipeline using [Meltano](https://meltano.com/).\n\n### Executing the Tap Directly\n\n- First create a file containing the configuration in a json format, e.g., config.json\n- Use the config file to create a catalog file and then invoke the tap\n\n```bash\ntap-feed --config config.json --discover > catalog.json\ntap-feed --config config.json --catalog catalog.json\n```\n\n',
    'author': 'Jon Watson',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jawats/tap-feed',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
