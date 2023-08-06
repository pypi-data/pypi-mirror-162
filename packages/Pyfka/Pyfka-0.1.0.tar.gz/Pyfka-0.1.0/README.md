# PyKafka
A python library to easily create kafka producer/consumer and manage topics

## Install

```shell
pip install PyKafka
```

## Setup
Use `docker-compose.yaml` file to start kafka service

```shell
docker-compose up -d
```

## Samples

### Producer

```python
from pykafka import PyKafkaConfig, PyKafkaTopic, producer

config = PyKafkaConfig(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "default",
        "auto.offset.reset": "earliest",
    }
)

my_topics = [
    PyKafkaTopic(name="my.topic1", partitions=[0]),
    PyKafkaTopic(name="my.topic2", partitions=[0, 1]),
]

@producer(
    topics=my_topics,
    config=config,
)
def my_producer(my_name: str):
    return {
        "name": my_name
    }

if __name__ == "__main__":
    my_producer("Jack")
    my_producer("Alice")

```