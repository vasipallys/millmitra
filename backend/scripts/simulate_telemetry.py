"""Publish sample dryer telemetry via HTTP ingest (default) or MQTT.

Usage (from backend/ with millmitra venv):

  python scripts/simulate_telemetry.py
  python scripts/simulate_telemetry.py --mqtt
  python scripts/simulate_telemetry.py --url http://127.0.0.1:5000 --token demo-device-token

MQTT requires MQTT_BROKER_URL and a running broker. HTTP ingest does not.
"""

import argparse
import json
import os
import random
import sys
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def post_http(base_url, token, metric, value):
    payload = json.dumps({
        'metric': metric,
        'value': value,
        'source': 'sensor',
        'tags': {'simulator': True},
    }).encode('utf-8')
    request = Request(
        base_url.rstrip('/') + '/api/iiot/ingest',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Device-Token': token,
        },
        method='POST',
    )
    with urlopen(request, timeout=10) as response:
        return response.status, response.read().decode('utf-8')


def publish_mqtt(broker_url, token, metric, value):
    import paho.mqtt.client as mqtt
    parsed = urlparse(broker_url if '://' in broker_url else 'mqtt://' + broker_url)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(parsed.hostname or '127.0.0.1', parsed.port or 1883, 30)
    client.publish('millmitra/telemetry', json.dumps({
        'token': token,
        'metric': metric,
        'value': value,
    }))
    client.disconnect()


def main():
    parser = argparse.ArgumentParser(description='MillMitra IIoT telemetry simulator')
    parser.add_argument('--url', default=os.environ.get('MILLMITRA_API', 'http://127.0.0.1:5000'))
    parser.add_argument('--token', default=os.environ.get('IOT_DEMO_TOKEN', 'demo-device-token'))
    parser.add_argument('--mqtt', action='store_true')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--sleep', type=float, default=1.0)
    args = parser.parse_args()

    metrics = (
        ('dryer_temp_c', 52.0, 8.0),
        ('moisture_pct', 13.5, 1.5),
        ('motor_amps', 11.0, 2.0),
    )
    for index in range(args.count):
        metric, base, spread = random.choice(metrics)
        value = round(base + random.uniform(-spread, spread), 2)
        if args.mqtt:
            broker = os.environ.get('MQTT_BROKER_URL')
            if not broker:
                print('MQTT_BROKER_URL is not set', file=sys.stderr)
                sys.exit(2)
            publish_mqtt(broker, args.token, metric, value)
            print('mqtt', metric, value)
        else:
            status, body = post_http(args.url, args.token, metric, value)
            print(status, metric, value, body[:120])
        if index + 1 < args.count:
            time.sleep(args.sleep)


if __name__ == '__main__':
    main()
