"""Optional MQTT subscriber. Never required to start the mill API."""

import json
import logging
import threading
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_THREAD = None


def _parse_broker(url):
    parsed = urlparse(url if '://' in url else 'mqtt://' + url)
    host = parsed.hostname or '127.0.0.1'
    port = parsed.port or 1883
    return host, port


def _on_message(app, _client, _userdata, message):
    try:
        payload = json.loads(message.payload.decode('utf-8'))
    except Exception:
        logger.info('iiot_mqtt_bad_payload')
        return
    token = payload.get('token') or payload.get('device_token')
    metric = payload.get('metric')
    value = payload.get('value')
    with app.app_context():
        from services import iiot_service
        device = iiot_service.device_by_token(token)
        if device is None:
            logger.info('iiot_mqtt_unknown_device')
            return
        iiot_service.ingest(device, metric, value, source='sensor', tags={'topic': message.topic})


def start_mqtt_subscriber(app):
    """Start a daemon thread only when MQTT_BROKER_URL is set."""
    global _THREAD
    url = (app.config.get('MQTT_BROKER_URL') or '').strip()
    if not url or app.config.get('TESTING'):
        return None
    if _THREAD and _THREAD.is_alive():
        return _THREAD
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        logger.info('iiot_mqtt_paho_missing')
        return None

    host, port = _parse_broker(url)

    def run():
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except Exception:
            client = mqtt.Client()
        client.on_message = lambda c, u, m: _on_message(app, c, u, m)

        def on_connect(client, _userdata, _flags, reason_code, _properties=None):
            if reason_code == 0 or reason_code == 'Success':
                client.subscribe('millmitra/+/+/+')
                client.subscribe('millmitra/telemetry')

        client.on_connect = on_connect
        try:
            client.connect(host, port, 60)
            client.loop_forever()
        except Exception:
            logger.info('iiot_mqtt_connect_failed host=%s', host)

    _THREAD = threading.Thread(target=run, name='millmitra-mqtt', daemon=True)
    _THREAD.start()
    logger.info('iiot_mqtt_started host=%s port=%s', host, port)
    return _THREAD
