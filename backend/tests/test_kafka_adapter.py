"""Kafka adapter unit test with a fake producer. No broker required."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.events import EventBus, KafkaAdapter, build_bus


class FakeProducer:
    def __init__(self):
        self.sent = []

    def send(self, topic, key=None, value=None):
        self.sent.append({'topic': topic, 'key': key, 'value': value})
        return True


class KafkaAdapterTests(unittest.TestCase):
    def test_publish_uses_injected_producer(self):
        producer = FakeProducer()
        adapter = KafkaAdapter('localhost:9092', producer=producer)
        adapter.publish('iiot.reading', {'topic': 'iiot.reading', 'payload': {'v': 1}})
        self.assertEqual(len(producer.sent), 1)
        self.assertEqual(producer.sent[0]['value']['payload']['v'], 1)

    def test_build_bus_prefers_fake_kafka(self):
        producer = FakeProducer()
        bus = build_bus(kafka_bootstrap='localhost:9092', kafka_producer=producer)
        bus.publish('demo', {'ok': True})
        self.assertEqual(producer.sent[0]['value']['topic'], 'demo')

    def test_missing_package_falls_back_to_memory(self):
        bus = EventBus()
        self.assertEqual(bus._adapter.name, 'memory')


if __name__ == '__main__':
    unittest.main()
