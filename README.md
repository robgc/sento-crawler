# Sento Crawler

_This project is part of Sento's backend_.

A concurrent tool designed for extracting and storing text from tweets about trending topics.

# Table of contents

# Prerequisites

In order to set up an instance you need a PostgreSQL database initialised
using the instructions available in [Sento API's readme](https://github.com/robgc/sento-api).

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

Follow these steps:

- Create a `config.ini` file from a copy of `config.example.ini` and adjust
the configuration according to your needs. If you use the PostgreSQL container
provided in Sento API instructions, let the default value of `sento-db` in
`[postgres].host`.

- Set your secrets in a `.env` file, make a copy of the `example.env` file.
  Keep in mind that you need a Twitter Developer account and a set of
  consumer API keys.

# License

The source code of this project is licensed under the GNU Affero General
Public License v3.0.
