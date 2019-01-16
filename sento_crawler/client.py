from peony import PeonyClient
from peony.oauth import OAuth2Headers

from sento_crawler.settings import config

_client = None  # type: PeonyClient


async def get_client():
    global _client
    if not _client:
        _client = PeonyClient(
            consumer_key=config.TWITTER_CONSUMER_API_KEY,
            consumer_secret=config.TWITTER_CONSUMER_API_SECRET_KEY,
            auth=OAuth2Headers
        )

    return _client


async def test():
    client = await get_client()
    return await client.api.trends.available.get()
