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


import json
import re
from datetime import datetime

import asyncpg
from dateutil import parser, tz

from sento_crawler.settings import get_config

_conn_pool = None  # type: asyncpg.pool.Pool
_url_regex = (
    r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b'
    r'([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
)


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

    async def get_relevant_trends_info(self):
        results = None  # type: asyncpg.Record
        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT
                  t.id AS id,
                  t.query_str AS query_str,
                  l.name AS location_name,
                  l.id AS woeid,
                  st_x (l.the_geom_point) AS longitude,
                  st_y (l.the_geom_point) AS latitude,
                  ceil(l.bcircle_radius / 1000) AS radius_km
                FROM ( SELECT DISTINCT
                    topic_id,
                    woeid
                  FROM
                    data.rankings
                  WHERE
                    ranking_ts BETWEEN now() - interval '12 hours'
                    AND now()) r
                  JOIN data.topics t ON r.topic_id = t.id
                  JOIN data.locations l ON r.woeid = l.id
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

    async def store_location(self, osm_data, twitter_data):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO data.locations
                      (id, the_geom, the_geom_point, name, osm_name)
                    VALUES (
                      $1,
                      ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON($2), 4326)),
                      ST_SetSRID(ST_MakePoint($3, $4), 4326),
                      $5,
                      $6
                    )
                    ON CONFLICT (id) DO NOTHING
                    """,
                    twitter_data.get('woeid'),
                    json.dumps(osm_data.get('geojson')),
                    float(osm_data.get('lon')),
                    float(osm_data.get('lat')),
                    twitter_data.get('name'),
                    osm_data.get('display_name')
                )

    async def store_tweets(self, tweets, trend_id, woeid):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.copy_records_to_table(
                    table_name='statuses',
                    records=[
                        (x.id,
                         parser.parse(x.created_at)
                         .astimezone(tz.tzutc()).replace(tzinfo=None),
                         datetime.utcnow(),
                         re.sub(_url_regex, '', x.text),
                         trend_id,
                         woeid) for x in tweets
                    ],
                    schema_name='data'
                )
