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


from yaml import load as yml_load
from typing import Dict


def _get_config() -> Dict[str, str]:
    result = None
    with open('config.yml') as cfg_file:
        result = yml_load(cfg_file)

    return result


_cfg = _get_config()


class Config:
    _twitter_consum_section = _cfg.get('twitter').get('consumer')

    TWITTER_CONSUMER_API_KEY = _twitter_consum_section.get('key')
    TWITTER_CONSUMER_API_SECRET_KEY = _twitter_consum_section.get('secret')

    LOGGING_LEVEL = _cfg.get('logging').get('level')
    LOGGING_OUTPUT = _cfg.get('logging').get('output')


config = Config()
