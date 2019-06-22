# Sento Crawler

_This project is part of Sento's backend_.

A concurrent tool designed for extracting and storing text from tweets about trending topics.

# Table of contents

# Prerequisites

In order to set up an instance you need a PostgreSQL database initialised previously
using the instructions available in [Sento API's readme](https://github.com/robgc/sento-api).

You also need a Twitter Developer account and a set of _Consumer API keys_ for your
Twitter Application.

# Executing the tool

## Choosing your environment

You have two options:

- Running the Docker container using Docker Compose: `docker-compose up -d`.
  You need the following software installed:
  - _Docker Engine 17.12.0 or greater required_.
  - _Docker Compose 1.18.0 or greater required_.

- Running locally on your machine, requiring:
  - Python 3.7 or greater.
  - Pipenv.

## Configuring the tool

Create a `config.ini` file from a copy of `config.example.ini` and adjust
the configuration according to your needs. If you use the PostgreSQL container
provided in Sento API instructions, let the default value of `sento-db` in the
`[postgres].host` section of your `config.ini`.

## Running the tool

- **With Docker**: run `docker-compose up -d`, this will compile the container image for you if
  you have not done it previously. If you make any changes to your `config.ini` after running
  the container you will need to stop it, remove it and recreate the container's image before
  creating another container instance. This container will try to connect
  to the `sento-net` Docker network, where the PostGIS container is listening for connections.

- **Running locally**:
  - Install the necessary dependencies in a virtual environment with `pipenv sync`.
  - Run the following command `pipenv run sento_api/main.py`, this will start Sento Crawler.

# License

The source code of this project is licensed under the GNU Affero General
Public License v3.0.
