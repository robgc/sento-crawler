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

FROM python:3.7.3-alpine3.9

WORKDIR /usr/src/app

ENV PYTHONPATH=${PYTHONPATH}:/usr/src/app

COPY Pipfile /usr/src/app
COPY Pipfile.lock /usr/src/app

RUN set -x \
    && apk add --no-cache postgresql-dev \
    && apk add --no-cache --virtual build-deps \
        make gcc g++ libffi-dev musl-dev \
    && pip install --no-cache-dir pipenv \
    && pipenv sync --clear \
    && apk del build-deps

COPY . /usr/src/app

CMD [ "pipenv", "run", "python", "sento_crawler/main.py" ]
