import asyncio

from sento_crawler.model import get_topics
from sento_crawler.logger import get_logger, get_queue_listener


async def main():
    logger = get_logger()
    logger.info('Launching Sento Crawler...')

    print(await get_topics())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        get_queue_listener().stop()
