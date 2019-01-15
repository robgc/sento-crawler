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


import os
from pathlib import Path

import yaml


def _get_config():
    result = None  # type: Dict[str, str]
    config_path = Path(__file__).parent.joinpath('config.yml')
    with open(config_path) as cfg_file:
        result = yaml.load(cfg_file)

    return result


_cfg = _get_config()


class Config:
    env = os.environ

    TWITTER_CONSUMER_API_KEY = env.get('TWITTER_CONSUMER_API_KEY')
    TWITTER_CONSUMER_API_SECRET_KEY = env.get(
        'TWITTER_CONSUMER_API_SECRET_KEY'
    )

    TWITTER_ACCESS_TOKEN = env.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = env.get('TWITTER_ACCESS_TOKEN_SECRET')

    LOGGING_LEVEL = _cfg.get('logging').get('level')
    ASYNCIO_LOGGING_LEVEL = _cfg.get('logging').get('asyncioLevel')
    LOGGING_OUTPUT = _cfg.get('logging').get('output')


config = Config()
