![Comlink logo](https://raw.githubusercontent.com/art1415926535/comlink/main/assets/logo.svg)

Send and receive messages by using SQS queues.


## Docs
### Example

```python
import asyncio
import datetime
from comlink import SqsConsumer, SqsQueue


async def example(sqs_client, queue_url):
    # Create a queue object
    sqs_queue = SqsQueue(url=queue_url, client=sqs_client)

    # Event for stopping the consumer
    stop_event = asyncio.Event()
    # Create a consumer with a handler that just prints the message
    consumer = SqsConsumer(queue=sqs_queue, handler=print)
    # Start the consumer
    consumer_task = await consumer.start(stop_event=stop_event)

    # Send a message to the queue
    await sqs_queue.put(f"{datetime.datetime.now()} Hello, world!")
    # Wait for 1 second for the message to be processed
    await asyncio.sleep(1)

    # Stop the consumer
    stop_event.set()
    # Wait for the consumer to stop
    await consumer_task
```

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