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


import logging
from pathlib import Path
from typing import Dict

from sento_crawler.settings import config

LOG_FORMAT = (
    '[%(levelname)s] - (%(asctime)s) || '
    '%(module)s - %(funcName)s - %(lineno)d || %(message)s'
)

VALID_OUTPUTS = (
    'console',
    'daily_rotating_file'
)


def _get_logging_settings() -> Dict:
    input_lvl = config.LOGGING_LEVEL
    input_out_dst = config.LOGGING_OUTPUT

    lvl = None
    out_dst = None

    if input_lvl == 'NOTSET':
        lvl = logging.NOTSET
    elif input_lvl == 'DEBUG':
        lvl = logging.DEBUG
    elif input_lvl == 'INFO':
        lvl = logging.INFO
    elif input_lvl == 'WARNING':
        lvl = logging.WARNING
    elif input_lvl == 'ERROR':
        lvl = logging.ERROR
    elif input_lvl == 'CRITICAL':
        lvl = logging.CRITICAL
    else:
        raise ValueError('A valid logging level must be set.')

    if input_out_dst in VALID_OUTPUTS:
        out_dst = input_out_dst
    else:
        raise ValueError('A valid logging output must be set.')

    return {
        'level': lvl,
        'output': out_dst
    }


_logging_cfg = _get_logging_settings()


logger = logging.getLogger()
logger.setLevel(_logging_cfg.get('level'))

logger_formatter = logging.Formatter(LOG_FORMAT)
logger_handler = None

if _logging_cfg.get('output') == VALID_OUTPUTS[0]:
    logger_handler = logging.StreamHandler()
else:
    logs_path = Path('./logs')
    logs_path.mkdir(exist_ok=True)

    logger_handler = logging.handlers.TimedRotatingFileHandler(
        filename='logs/sento_crawler.log',
        when='midnight',
        utc=True
    )

logger_handler.setLevel(_logging_cfg.get('level'))
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
