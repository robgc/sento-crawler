# Copyright (C) 2019 Roberto García Calero (garcalrob@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import aiohttp

from peony import PeonyClient, task

from sento_crawler.logger import get_logger
from sento_crawler.model import Model
from sento_crawler.settings import get_config

NOMINATIM_SEARCH_URL = 'https://nominatim.openstreetmap.org/search'


class TwitterClient(PeonyClient):
    @classmethod
    async def create(cls):
        cls.model = Model()
        cls.logger = get_logger()
        cls.search_woeid = get_config().SEARCH_WOEID
        await cls.model.create()

    async def _get_locations_with_trends(self):
        """Returns the locations that have trends in the moment when the
        request is made and whose parent woeid is the specified in the
        configuration file

        Returns
        -------
        list of PeonyResponse
            The locations with trends
        """
        self.logger.debug('Requesting trends/available')

        locations = await self.api.trends.available.get()
        return [_ for _ in locations if _.parentid == self.search_woeid]

    async def _get_location_information(self, location):
        location_exists = (
            await self.model.check_location_existence(location.get('woeid'))
        )
        if not location_exists:
            self.logger.debug(
                'Requesting location data for %s (WOEID %d)',
                location.get('name'),
                location.get('woeid')
            )

            async with aiohttp.ClientSession() as session:
                params = {
                    'format': 'json',
                    'city': location.get('name'),
                    'polygon_geojson': 1,
                    'country': location.get('country'),
                    'limit': 1
                }

                async with session.get(
                    NOMINATIM_SEARCH_URL,
                    params=params
                ) as resp:
                    data = await resp.json()
                    osm_data = data[0] if data else None

                    self.logger.debug(
                        'Storing location data for %s (WOEID %d) [%s, %s]',
                        osm_data.get('display_name'),
                        location.get('woeid'),
                        osm_data.get('lon'),
                        osm_data.get('lat')
                    )

                    await self.model.store_location(osm_data, location)

    async def _get_trends_for_location(self, location):
        self.logger.debug(
            'Requesting trends and location data for '
            '%s WOEID: %d Country: %s',
            location.name,
            location.woeid,
            location.country
        )

        trends_response, location_info = await asyncio.gather(
            self.api.trends.place.get(id=location.woeid),
            self._get_location_information(location)
        )

        # Get the trends from the response
        trends = trends_response.data[0].get('trends')

        self.logger.debug(
            'Storing trends and location info for %s WOEID: %d Country: %s',
            location.name,
            location.woeid,
            location.country
        )

        await self.model.store_trends(location.woeid, trends)

    @task
    async def get_trends(self):
        try:
            while True:
                self.logger.debug('Looking for trends')

                locations = await self._get_locations_with_trends()
                coros = [self._get_trends_for_location(_) for _ in locations]

                self.logger.debug('Launching trends extraction coroutines '
                                  'for each location')

                await asyncio.gather(*coros)

                self.logger.debug('Sleeping')

                await asyncio.sleep(15 * 60)
        except Exception as err:
            self.logger.error(f'Exception ocurred in get_trends task: {err}')

    @task
    async def get_tweets(self):
        self.logger.debug('Extracting tweets for trends')

        relevant_trends = await self.model.get_relevant_trends_info()

        while not relevant_trends:
            await asyncio.sleep(5)
            relevant_trends = await self.model.get_relevant_trends_info()

        coros = [self._get_tweets_from_trend(_) for _ in relevant_trends]

        await asyncio.gather(*coros)

    # TODO: Finish model `store_tweets` and test the since_id iterator

    async def _get_tweets_from_trend(self, trend):
        self.logger.debug(
            'Extracting tweets from trend "%s" written in %s',
            trend.get('id'),
            trend.get('location_name')
        )

        geocode_str = (
            f'{trend.get("latitude")},'
            f'{trend.get("longitude")},'
            f'{trend.get("radius_km")}km'
        )

        # TODO: Make locale configurable

        req_params = {
            'q': trend.get('query_str'),
            'geocode': geocode_str,
            'result_type': 'recent',
            'count': 100,
            'locale': 'es'
        }

        req = self.api.search.tweets.get(**req_params)
        responses = req.iterator.with_since_id()

        async for tweets in responses:
            await self.model.store_tweets(
                tweets, trend.get('id'), trend.get('woeid')
            )
