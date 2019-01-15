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
import time
from logging.handlers import (QueueHandler, QueueListener,
                              TimedRotatingFileHandler)
from pathlib import Path
from queue import Queue

from sento_crawler.settings import config

LOG_FORMAT = (
    '%(asctime)-23s %(levelname)-8s '
    '%(module)s::%(funcName)s::%(lineno)d || %(message)s'
)

VALID_OUTPUTS = (
    'console',
    'daily_rotating_file'
)

_logger = None  # type: logging.Logger
_queue_listener = None  # type: logging.handlers.QueueListener


def _get_logging_settings():
    input_lvl = config.LOGGING_LEVEL
    input_asyncio_lvl = config.ASYNCIO_LOGGING_LEVEL
    input_out_dst = config.LOGGING_OUTPUT

    lvl = logging.getLevelName(input_lvl)
    asyncio_lvl = logging.getLevelName(input_asyncio_lvl)
    out_dst = None  # type: str

    if input_out_dst in VALID_OUTPUTS:
        out_dst = input_out_dst
    else:
        raise ValueError('A valid logging output must be set.')

    return {
        'level': lvl,
        'asyncio_level': asyncio_lvl,
        'output': out_dst
    }


def _setup_logging():
    global _logger
    global _queue_listener

    logging_cfg = _get_logging_settings()
    log_queue = Queue(-1)

    _logger = logging.getLogger('sento-crawler')
    asyncio_logger = logging.getLogger('asyncio')

    _logger.setLevel(logging_cfg.get('level'))
    asyncio_logger.setLevel(logging_cfg.get('asyncio_level'))

    logger_formatter = logging.Formatter(LOG_FORMAT)
    logger_formatter.converter = time.gmtime
    out_handler = None  # type: logging.Handler

    if logging_cfg.get('output') == VALID_OUTPUTS[0]:
        out_handler = logging.StreamHandler()
    else:
        logs_path = Path('./logs')
        logs_path.mkdir(exist_ok=True)

        out_handler = TimedRotatingFileHandler(
            filename='logs/sento_crawler.log',
            when='midnight',
            utc=True
        )

    out_handler.setLevel(logging.INFO)
    out_handler.setFormatter(logger_formatter)

    logger_handler = QueueHandler(log_queue)
    _queue_listener = QueueListener(log_queue, out_handler)

    _logger.addHandler(logger_handler)
    asyncio_logger.addHandler(logger_handler)

    # The queue listener must be stopped when execution finishes
    # This line spawns a listener in another thread!
    _queue_listener.start()


def get_logger():
    if _logger is None:
        _setup_logging()
    return _logger


def get_queue_listener():
    if _queue_listener is None:
        _setup_logging()
    return _queue_listener
