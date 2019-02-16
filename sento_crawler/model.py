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


from datetime import datetime

import asyncpg

from sento_crawler.settings import get_config

_conn_pool = None  # type: asyncpg.pool.Pool


async def _get_conn_pool():
    global _conn_pool
    config = get_config()
    if _conn_pool is None:
        _conn_pool = await asyncpg.create_pool(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWD,
            database='sento'
        )
    return _conn_pool


class Model:
    @classmethod
    async def create(cls):
        cls.pool = await _get_conn_pool()

    async def store_trends(self, location_woeid, trends):
        for idx, trend in enumerate(trends):
            async with self.pool.acquire() as conn:
                # Insert trend data if it does not exist on one transaction
                async with conn.transaction():
                    await conn.execute(
                        """
                        INSERT INTO data.topics (id, url, query_str)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        trend.name,
                        trend.url,
                        trend.query
                    )

                # Insert trend's ranking data for the current location
                # in another transaction
                async with conn.transaction():
                    await conn.execute(
                        """
                        INSERT INTO data.rankings
                        (ranking_ts, ranking_no, woeid, tweet_volume, topic_id)
                        VALUES
                        ($1, $2, $3, $4, $5)
                        """,
                        datetime.utcnow(),
                        idx + 1,
                        location_woeid,
                        trend.tweet_volume,
                        trend.name
                    )

    async def get_relevant_topics(self):
        results = None  # type: asyncpg.Record
        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT
                  t.id AS id,
                  t.query_str AS query_str
                FROM
                  data.rankings r
                  JOIN data.topics t ON r.topic_id = t.id
                WHERE
                  r.ranking_ts BETWEEN now() - interval '1DAY'
                  AND now()
                GROUP BY
                  t.id,
                  t.query_str
                """
            )
        return results

    async def check_location_existence(self, woeid):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                SELECT
                  exists(
                    SELECT 1
                    FROM
                      data.locations l
                    WHERE
                      l.id = $1
                  )
                """,
                woeid
            )

    async def store_location(self, geo_data, twitter_data):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO data.locations
                      (id, the_geom, coords, name, geo_name)
                    VALUES
                      ($1, ST_SetSRID(ST_GeomFromGeoJSON($2), 4326),
                       ST_SetSRID(ST_MakePoint($3, $4), 4326),
                       $5, $6
                    ON CONFLICT (id) DO NOTHING
                    """,
                    twitter_data.get('woeid'),
                    geo_data.get('geojson'),
                    geo_data.get('lon'),
                    geo_data.get('lat'),
                    twitter_data.get('name'),
                    geo_data.get('display_name')
                )



    # async def get_since_id(self, topic_id):
    #     result = None
    #     async with self.pool.acquire() as conn:
    #         result = await conn.fetchval(
    #             """

    #             """

    #         )
