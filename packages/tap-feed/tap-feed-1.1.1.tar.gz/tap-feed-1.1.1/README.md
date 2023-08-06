[![Tests](https://github.com/jawats/tap-feed/actions/workflows/tests.yml/badge.svg)](https://github.com/jawats/tap-feed/actions/workflows/tests.yml)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 

# tap-feed

`tap-feed` is a Singer tap for various feeds and was built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.
This tap can be used with RSS and Atom based feeds thanks to [feedparser](https://feedparser.readthedocs.io/en/latest/index.html).

## Installation

To install this tap, simply run the following command in your terminal:

```bash
pipx install tap-feed
```

Or if you don't want to use pipx:

```bash
pip3 install tap-feed
```

## Configuration

### Accepted Config Options

| Property                   | Type             | Required? | Description                                                                |
| ---                        | ---              | ---       | ---                                                                        |
| feed_urls                  | String           | Yes       | A list of one or more feed paths                                           |
| feed_fields                 | Array of Strings | Yes       | A list of feed level data fields to capture                                 |
| feed_entry_fields           | Array of Strings | Yes       | A list of entry level data fields to capture                                |
| feed_entry_replication_key | String           | Yes       | The field used to determine new records, typically 'published' or 'updated' |
| start_date                 | Date Time        | No        | The earliest record date to sync                                           |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-feed --about
```

### Example Config File
```json
{
  "feed_urls": ["http://feeds.feedburner.com/PythonSoftwareFoundationNews", "https://talkpython.fm/episodes/rss"],
  "feed_fields": ["title", "subtitle"],
  "feed_entry_fields": ["id", "title", "link"],
  "feed_entry_replication_key": "published"
}
```

## Usage

You can easily run `tap-feed` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

- First create a file containing the configuration in a json format, e.g., config.json
- Use the config file to create a catalog file and then invoke the tap

```bash
tap-feed --config config.json --discover > catalog.json
tap-feed --config config.json --catalog catalog.json
```

