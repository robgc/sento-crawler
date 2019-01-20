import asyncio

from peony.oauth import OAuth2Headers

from sento_crawler.client import TwitterClient
from sento_crawler.logger import get_logger, get_queue_listener
from sento_crawler.settings import get_config


async def main():
    logger = get_logger()
    logger.info('Launching Sento Crawler...')

    config = get_config()

    client = TwitterClient(
        consumer_key=config.TWITTER_CONSUMER_API_KEY,
        consumer_secret=config.TWITTER_CONSUMER_API_SECRET_KEY,
        auth=OAuth2Headers
    )

    await client.twitter_configuration
    await client.create()
    await client.run_tasks()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        get_queue_listener().stop()
