# Copyright (C) 2018 Roberto García Calero (garcalrob@gmail.com)
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


from configparser import ConfigParser
from pathlib import Path

_config = None  # type: Config


class Config:
    def __init__(self):
        parser = ConfigParser()
        config_path = (
            Path(__file__)
            .absolute()
            .parents[1]
            .joinpath('config.ini')
        )
        parser.read(config_path)

        # Logging
        self.LOGGING_LEVEL = parser['logging'].get('level')
        self.ASYNCIO_LOGGING_LEVEL = parser['logging'].get('asyncioLevel')
        self.PEONY_TWITTER_LOGGING_LEVEL = (
            parser['logging'].get('peonyTwitterLevel')
        )
        self.LOGGING_OUTPUT = parser['logging'].get('output')

        # Postgres
        self.POSTGRES_HOST = parser['postgres'].get('host', 'postgres')
        self.POSTGRES_PORT = int(parser['postgres'].get('port', 5432))
        self.POSTGRES_DATABASE = parser['postgres'].get('database', 'sento')
        self.POSTGRES_USER = parser['postgres'].get('user', 'sento')
        self.POSTGRES_PASSWD = parser['postgres'].get('password', 'sento')

        # app config
        self.SEARCH_WOEID = int(parser['app'].get('woeid'))

        # Twitter
        self.TWITTER_CONSUMER_API_KEY = (
            parser['twitter'].get('consumer_api_key')
        )
        self.TWITTER_CONSUMER_API_SECRET_KEY = (
            parser['twitter'].get('consumer_api_secret_key')
        )


def get_config():
    global _config
    if _config is None:
        _config = Config()
    return _config
