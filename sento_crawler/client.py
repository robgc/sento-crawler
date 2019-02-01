import asyncio

from peony import PeonyClient, task

from sento_crawler.logger import get_logger
from sento_crawler.model import Model
from sento_crawler.settings import get_config


class TwitterClient(PeonyClient):
    @classmethod
    async def create(cls):
        cls.model = Model()
        cls.logger = get_logger()
        cls.search_woeid = get_config().SEARCH_WOEID
        await cls.model.create()

    async def _get_locations_with_trends(self):
        self.logger.debug('Requesting trends/available...')

        locations = await self.api.trends.available.get()
        return [_ for _ in locations if _.parentid == self.search_woeid]

    @task
    async def get_trends(self):
        self.logger.debug('Looking for trends...')

        locations = await self._get_locations_with_trends()
        for location in locations:
            self.logger.debug(
                'Requesting trends data for '
                '%s WOEID: %d Country: %s',
                location.name,
                location.woeid,
                location.country
            )

            response = await self.api.trends.place.get(id=location.woeid)
            # Get the trends from the response
            trends = response.data[0].get('trends')

            self.logger.debug(
                'Storing trends info for '
                '%s WOEID: %d Country: %s',
                location.name,
                location.woeid,
                location.country
            )

            await self.model.store_trends(location.woeid, trends)
        self.logger.debug('Sleeping...')
        asyncio.sleep(15 * 60)
