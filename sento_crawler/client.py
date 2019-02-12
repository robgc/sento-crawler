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
        self.logger.debug('Requesting trends/available...')

        locations = await self.api.trends.available.get()
        return [_ for _ in locations if _.parentid == self.search_woeid]

    async def _get_location_information(self, location):
        self.logger.debug(
            'Requesting location data for %s (WOEID %d)',
            location.name,
            location.woeid
        )

        async with aiohttp.ClientSession() as session:
            params = {
                'format': 'json',
                'city': location.name,
                'polygon_geojson': 1,
                'country': location.country,
                'limit': 1
            }

            async with session.get(
                NOMINATIM_SEARCH_URL,
                params=params
            ) as resp:
                data = (await resp.json())[0]
                # TODO: Store location information
                self.logger.debug(
                    'Location data obtained: Place: %s OSM ID: %s Type: %s '
                    'Coords: %s',
                    data.get('display_name'),
                    data.get('osm_id'),
                    data.get('type'),
                    f"{data.get('lon')}, {data.get('lat')}"
                )

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
        while True:
            self.logger.debug('Looking for trends...')
            locations = await self._get_locations_with_trends()

            coros = [self._get_trends_for_location(_) for _ in locations]

            self.logger.debug('Launching trends extraction coroutines '
                              'for each location...')
            await asyncio.gather(*coros)

            self.logger.debug('Sleeping...')
            await asyncio.sleep(15 * 60)

    # TODO: Finish this task

    # @task
    # async def get_tweets(self):
    #     self.logger.debug('Extracting tweets for trends...')

    #     while True:
    #         relevant_topics = await self.model.get_relevant_topics()
    #         if relevant_topics:
    #             break
    #         else:
    #             await asyncio.sleep(30)

    #     for topic in relevant_topics:
    #         req_params = {
    #             'q': topic.query_str,
    #             'result_type': 'recent',
    #             'count': 100
    #         }
    #         req = self.api.search.tweets.get(
    #             q=topic.query_str,
    #             result_type='recent',
    #             count=100
    #         )
