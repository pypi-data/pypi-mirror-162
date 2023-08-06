"""Stream type classes for tap-feed."""

from typing import List, Iterable, Optional

from dateutil import parser as datetime_parser
import feedparser  # type: ignore
import requests
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.streams import RESTStream


class FeedStream(RESTStream):
    """FeedStream class."""

    url_base = ""
    name = "feed"
    path = ""
    primary_keys = ["entry_id"]
    replication_key = ""

    @property
    def schema(self) -> dict:
        """Create a dynamic schema based on the tap configuration provided."""
        feed_properties: list = [
            th.Property("feed_url", th.StringType),
        ]
        feed_properties.extend(
            [
                th.Property(f"feed_{name}", th.StringType)
                for name in self.config["feed_fields"]
            ]
        )
        feed_properties.extend(
            [
                th.Property("entry_id", th.StringType),
                th.Property(FeedStream.replication_key, th.DateTimeType),
            ]
        )
        feed_properties.extend(
            [
                th.Property(f"entry_{name}", th.StringType)
                for name in self.config["feed_entry_fields"]
                if name not in ["id", "published", "updated"]
            ]
        )
        return th.PropertiesList(*feed_properties).to_dict()

    @property
    def partitions(self) -> Optional[List[dict]]:
        """Return a list of partition key dicts for the feed URLs."""
        return [{"feed_url": url} for url in self.config["feed_urls"]]

    def get_url(self, context: Optional[dict]) -> str:
        """Get the stream entity URL for the current partition."""
        partition = context or {}
        return partition["feed_url"]

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        feed = feedparser.parse(response.text)
        rep_key = FeedStream.replication_key[6:]
        entries = sorted(
            feed["entries"], key=lambda d: datetime_parser.parse(d[rep_key])
        )
        feed_url = response.url
        bookmark_timestamp = self.get_starting_timestamp({"feed_url": feed_url})
        for entry in entries:
            published_str = entry.get(rep_key)
            if published_str is None:
                continue
            published_date = datetime_parser.parse(published_str)
            if bookmark_timestamp is None or published_date > bookmark_timestamp:
                record = {"feed_url": feed_url}
                record.update(
                    {
                        f"feed_{name}": feed["feed"].get(name)
                        for name in self.config["feed_fields"]
                    }
                )
                record.update(
                    {
                        "entry_id": entry["id"],
                        FeedStream.replication_key: str(published_date),
                    }
                )
                record.update(
                    {
                        f"entry_{name}": entry.get(name)
                        for name in self.config["feed_entry_fields"]
                        if name not in ["id", "published", "updated"]
                    }
                )
                yield record
