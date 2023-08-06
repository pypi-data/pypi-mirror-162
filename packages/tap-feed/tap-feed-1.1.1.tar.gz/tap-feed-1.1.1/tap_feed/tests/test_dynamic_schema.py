"""Tests the schema that is dynamically generated from the configuration"""
import pytest
from singer_sdk.tap_base import Tap

from tap_feed.tap import TapFeed


@pytest.mark.parametrize(
    "configuration,expected_schema_keys",
    [
        (
            {
                "feed_urls": [
                    "http://feeds.feedburner.com/PythonSoftwareFoundationNews"
                ],
                "feed_fields": ["title", "subtitle"],
                "feed_entry_fields": ["id", "title", "summary", "link"],
            },
            [
                "feed_url",
                "feed_title",
                "feed_subtitle",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_summary",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": [
                    "http://feeds.feedburner.com/PythonSoftwareFoundationNews"
                ],
                "feed_fields": ["title", "subtitle"],
                "feed_entry_fields": ["published", "title", "summary", "link"],
            },
            [
                "feed_url",
                "feed_title",
                "feed_subtitle",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_summary",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": [
                    "http://feeds.feedburner.com/PythonSoftwareFoundationNews"
                ],
                "feed_fields": ["title"],
                "feed_entry_fields": ["title", "summary"],
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_summary",
            ],
        ),
        (
            {
                "feed_urls": [
                    "http://feeds.feedburner.com/PythonSoftwareFoundationNews"
                ],
                "feed_fields": ["language", "title"],
                "feed_entry_fields": ["title", "episode", "description"],
            },
            [
                "feed_url",
                "feed_language",
                "feed_title",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_episode",
                "entry_description",
            ],
        ),
        (
            {
                "feed_urls": [
                    "http://feeds.feedburner.com/PythonSoftwareFoundationNews"
                ],
                "feed_fields": ["language", "title"],
                "feed_entry_fields": ["title", "episode", "description"],
                "feed_entry_replication_key": "updated",
            },
            [
                "feed_url",
                "feed_language",
                "feed_title",
                "entry_id",
                "entry_updated",
                "entry_title",
                "entry_episode",
                "entry_description",
            ],
        ),
    ],
)
def test_schema_generated(configuration, expected_schema_keys):
    """Verifies the schema is generated correctly from the configuration provided"""
    test_tap: Tap = TapFeed(config=configuration)
    test_tap.run_discovery()
    catalog = test_tap.catalog_dict
    assert (
        list(catalog["streams"][0]["schema"]["properties"].keys())
        == expected_schema_keys
    )
