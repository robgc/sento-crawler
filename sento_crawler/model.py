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

    async def get_topics(self):
        return await self.pool.fetch('SELECT * FROM data.topics')
