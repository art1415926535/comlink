![Comlink logo](./assets/logo.svg)

Send and receive messages by using SQS queues.


## Development

### Setup

1. Install [Poetry](https://python-poetry.org/).
1. Install dependencies with `poetry install`.
1. Install [Docker](https://www.docker.com/).
1. Run `docker compose -f docker-compose.dev.yml up -d` to start 
the development environment (localstack). Tests will fail until the environment is up and running.


### Testing

Run `poetry run pytest` to run the tests.


### Formatting

Run `poetry run black .` to format the code.

Run `poetry run isort .` to sort the imports.