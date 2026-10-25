"""In-process event bus with pluggable adapters. App starts without Redis."""

import json
import logging
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._adapter = InMemoryAdapter()

    def use(self, adapter):
        if adapter is not None:
            self._adapter = adapter

    def subscribe(self, topic, handler):
        self._handlers[topic].append(handler)

    def publish(self, topic, payload):
        event = {'topic': topic, 'payload': payload or {}}
        try:
            self._adapter.publish(topic, event)
        except Exception:
            logger.exception('event_bus_adapter_failed topic=%s', topic)
        for handler in list(self._handlers.get(topic, [])):
            try:
                handler(event)
            except Exception:
                logger.exception('event_bus_handler_failed topic=%s', topic)
        return event


class InMemoryAdapter:
    name = 'memory'

    def __init__(self):
        self.messages = []
        self._lock = threading.Lock()

    def publish(self, topic, event):
        with self._lock:
            self.messages.append((topic, event))


class RedisStreamsAdapter:
    name = 'redis-streams'

    def __init__(self, redis_url, stream='millmitra.events'):
        import redis
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.stream = stream

    def publish(self, topic, event):
        self._client.xadd(self.stream, {
            'topic': topic,
            'payload': json.dumps(event.get('payload') or {}, default=str),
        })


class KafkaAdapter:
    """Real Kafka adapter. Lazy-imports kafka-python-ng / kafka-python.

    App starts without the package or a broker. Not integration-tested here.
    Inject ``producer`` in unit tests.
    """

    name = 'kafka'

    def __init__(self, bootstrap_servers, producer=None, topic='millmitra.events'):
        self.topic = topic
        if producer is not None:
            self._producer = producer
            return
        from kafka import KafkaProducer
        servers = [part.strip() for part in str(bootstrap_servers).split(',') if part.strip()]
        self._producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda value: json.dumps(value, default=str).encode('utf-8'),
        )

    def publish(self, topic, event):
        key = (topic or self.topic).encode('utf-8')
        self._producer.send(self.topic, key=key, value=event)


def build_bus(redis_url=None, kafka_bootstrap=None, kafka_producer=None):
    bus = EventBus()
    if kafka_bootstrap or kafka_producer is not None:
        try:
            bus.use(KafkaAdapter(kafka_bootstrap, producer=kafka_producer))
            return bus
        except Exception:
            logger.info('event_bus_kafka_unavailable')
    if redis_url:
        try:
            bus.use(RedisStreamsAdapter(redis_url))
        except Exception:
            logger.info('event_bus_redis_unavailable')
    return bus


BUS = EventBus()
