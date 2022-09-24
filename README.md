![Comlink logo](https://raw.githubusercontent.com/art1415926535/comlink/main/assets/logo.svg)

Send and receive messages by using SQS queues.

[![PyPI version](https://badge.fury.io/py/comlink.svg)](https://pypi.org/project/comlink)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/comlink)](https://pypi.org/project/comlink)
[![PyPI - License](https://img.shields.io/pypi/l/comlink)](https://github.com/art1415926535/comlink/blob/main/LICENSE)

```bash
pip install comlink
```

```bash
poetry add comlink
```

## Example

```python
from comlink import SqsConsumer, SqsQueue, signal_event


async def example(queue_url, sqs_client):
    # Create a queue object
    sqs_queue = SqsQueue(url=queue_url, client=sqs_client)

    # Event for stopping the consumer by receiving os signal.
    # stop_event waits for SIGINT(Ctrl+C) or SIGTERM by default
    stop_event = signal_event()
    # Create a consumer with a handler that just prints the message
    consumer = SqsConsumer(queue=sqs_queue, handler=print)
    # Start the consumer
    consumer_task = await consumer.start(stop_event=stop_event)

    # Send a message to the queue
    await sqs_queue.put("Hello, world!")

    # Wait for the consumer to stop by receiving os signal
    await consumer_task
```

More examples can be found in the [examples](https://github.com/art1415926535/comlink/tree/main/examples) directory.

## Docs
[SqsQueue](#comlinksqsqueueurl-client-serializernone-deserializernone)
* [coroutine put(data, **kwargs)](#coroutine-putdata-kwargs)
* [coroutine take(max_messages, visibility_timeout, wait_time_seconds, **kwargs)](#coroutine-takemax_messages-visibility_timeout-wait_time_seconds-kwargs)
* [remove(receipt_handle, **kwargs)](#coroutine-removereceipt_handle-kwargs)

<hr>


### `comlink.SqsQueue(url, client, serializer=None, deserializer=None)`
It is a wrapper around aiobotocore's SQS client. It provides a simple interface for sending and receiving messages.

In most cases, you will need to pass a instance of this class to the `comlink.SqsConsumer` and send messages to it using the `put` method.

`take` and `remove` methods are used by the `SqsConsumer` class. But you can use them if you need to.

Parameters:
* `url: str` - URL of the queue
* `client: Any` - aiobotocore's SQS client
* `serializer: Callable[[Message], str] | None` - a function that serializes the message to string
* `deserializer: Callable[[str], Message] | None` - a function that deserializes the message from string

#### Example
```python

import json
from comlink import SqsQueue

async def example(queue_url, sqs_client):
    sqs_queue = SqsQueue(url=queue_url, client=sqs_client, serializer=json.dumps, deserializer=json.loads)

    await sqs_queue.put({"hello": "world"})
    
    message = await sqs_queue.take(max_messages=1, visibility_timeout=10, wait_time_seconds=0)
    print(message[0]["Body"])
    
    await sqs_queue.remove(message[0]["ReceiptHandle"])
```
<hr>

#### coroutine `put(data, **kwargs)`
Sends a message to the queue.  
Parameters:
* `data: Message` - message data. If `serializer` is provided, it will be called with `data` as an argument.
* `kwargs` - additional arguments for aiobotocore's `send_message` method. E.g. `DelaySeconds`, `MessageGroupId`, `MessageDeduplicationId` and etc.

Returns result of aiobotocore's `send_message` method.
<hr>

#### coroutine `take(max_messages, visibility_timeout, wait_time_seconds, **kwargs)`
Get messages from the queue.  
Parameters:
* `max_messages: int` - maximum number of messages to receive
* `visibility_timeout: int` - the duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved by a `take` request
* `wait_time_seconds: int` - the duration (in seconds) for which the call waits for a message to arrive in the queue before returning. If a message is available, the call returns sooner than `wait_time_seconds`. If no messages are available and the wait time expires, the call returns successfully with an empty list of messages.
* `kwargs` - additional arguments for aiobotocore's `receive_message` method. E.g. `AttributeNames`, `MessageAttributeNames` and etc.

Returns list of messages that were received from the queue.
<hr>

#### coroutine `remove(receipt_handle, **kwargs)`
Deletes the specified message from the queue.  
Parameters:
* `receipt_handle: str` - the receipt handle associated with the message to delete (from `take` method)

Returns result of aiobotocore's `delete_message` method.


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