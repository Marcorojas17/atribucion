"""
Atribución Robotics — Driver MQTT.

Comunicación con robots vía MQTT (Message Queuing Telemetry Transport).
Requiere `paho-mqtt` instalado (pip install paho-mqtt).

Uso:
    driver = MQTTDriver(broker="broker.hivemq.com", port=1883)
    driver.publish("robots/robot-001/status", {"battery": 85})
    driver.shutdown()
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class MQTTConfig:
    """Configuración del cliente MQTT."""

    broker: str = "localhost"
    port: int = 1883
    client_id: str = "atribucion-robot"
    username: str | None = None
    password: str | None = None
    keepalive: int = 60
    qos: int = 1
    tls: bool = False


class MQTTDriver:
    """Driver para MQTT."""

    def __init__(self, config: MQTTConfig | None = None) -> None:
        if not MQTT_AVAILABLE:
            raise RuntimeError(
                "paho-mqtt no instalado. pip install paho-mqtt"
            )

        self.config = config or MQTTConfig()
        self.client = mqtt.Client(client_id=self.config.client_id)

        if self.config.username:
            self.client.username_pw_set(
                self.config.username,
                self.config.password,
            )

        if self.config.tls:
            self.client.tls_set()

        self._handlers: dict[str, Callable[[dict[str, Any]], None]] = {}
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        logger.info("Conectando a MQTT %s:%d...", self.config.broker, self.config.port)
        self.client.connect(self.config.broker, self.config.port, self.config.keepalive)
        self.client.loop_start()

    # ─── CALLBACKS ─────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            logger.info("MQTT conectado")
        else:
            logger.error("MQTT error de conexión: %d", rc)

    def _on_disconnect(self, client, userdata, rc) -> None:
        logger.warning("MQTT desconectado (rc=%d)", rc)

    def _on_message(self, client, userdata, msg) -> None:
        topic = msg.topic
        handler = self._handlers.get(topic)
        if not handler:
            return
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            handler(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("Mensaje inválido en %s: %s", topic, e)

    # ─── PUBLISH ───────────────────────────────────────────────

    def publish(
        self,
        topic: str,
        data: dict[str, Any],
        retain: bool = False,
    ) -> None:
        """Publica un mensaje JSON en un topic."""
        payload = json.dumps(data, ensure_ascii=False)
        self.client.publish(
            topic,
            payload,
            qos=self.config.qos,
            retain=retain,
        )
        logger.debug("MQTT publicado: %s → %s", topic, payload[:100])

    # ─── SUBSCRIBE ─────────────────────────────────────────────

    def subscribe(
        self,
        topic: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """Suscribe a un topic con un handler JSON."""
        self._handlers[topic] = handler
        self.client.subscribe(topic, qos=self.config.qos)
        logger.info("MQTT suscrito a %s", topic)

    def unsubscribe(self, topic: str) -> None:
        """Cancela suscripción."""
        self._handlers.pop(topic, None)
        self.client.unsubscribe(topic)

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def shutdown(self) -> None:
        """Cierra el cliente MQTT."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT cerrado")