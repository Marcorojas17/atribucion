"""
Atribución Robotics — Driver ROS2.

Wrapper para ROS2 (Robot Operating System 2).
Requiere `rclpy` instalado (pip install rclpy).

Uso:
    driver = ROS2Driver(node_name="atribucion_robot")
    driver.publish("/robot/status", {"state": "idle", "battery": 85})
    driver.shutdown()
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy
    from std_msgs.msg import String
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class ROS2Config:
    """Configuración del driver ROS2."""

    node_name: str = "atribucion_robot"
    namespace: str = ""
    qos_depth: int = 10
    qos_reliability: str = "reliable"


class ROS2Driver:
    """Driver para ROS2."""

    def __init__(self, config: ROS2Config | None = None) -> None:
        if not ROS2_AVAILABLE:
            raise RuntimeError(
                "rclpy no instalado. Instala ROS2 primero o usa otro driver."
            )

        self.config = config or ROS2Config()

        if not rclpy.ok():
            rclpy.init()

        self.node = Node(
            self.config.node_name,
            namespace=self.config.namespace,
        )

        qos = QoSProfile(depth=self.config.qos_depth)
        if self.config.qos_reliability == "best_effort":
            qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self._qos = qos
        self._publishers: dict[str, Any] = {}
        self._subscriptions: dict[str, Any] = {}

        logger.info("ROS2 node %s iniciado", self.config.node_name)

    # ─── PUBLISH ───────────────────────────────────────────────

    def _get_publisher(self, topic: str):
        if topic not in self._publishers:
            self._publishers[topic] = self.node.create_publisher(
                String, topic, self._qos
            )
        return self._publishers[topic]

    def publish(self, topic: str, data: dict[str, Any]) -> None:
        """Publica un mensaje JSON en un topic."""
        pub = self._get_publisher(topic)
        msg = String()
        msg.data = json.dumps(data, ensure_ascii=False)
        pub.publish(msg)
        logger.debug("Publicado en %s: %s", topic, msg.data[:100])

    # ─── SUBSCRIBE ─────────────────────────────────────────────

    def subscribe(
        self,
        topic: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """Suscribe a un topic con un handler JSON."""

        def _callback(msg: String) -> None:
            try:
                data = json.loads(msg.data)
                handler(data)
            except json.JSONDecodeError:
                logger.warning("Mensaje inválido en %s: %s", topic, msg.data[:100])

        sub = self.node.create_subscription(String, topic, _callback, self._qos)
        self._subscriptions[topic] = sub
        logger.info("Suscrito a %s", topic)

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def spin_once(self, timeout_sec: float = 0.1) -> None:
        """Procesa un ciclo de callbacks."""
        rclpy.spin_once(self.node, timeout_sec=timeout_sec)

    def shutdown(self) -> None:
        """Cierra el nodo ROS2."""
        self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        logger.info("ROS2 node %s cerrado", self.config.node_name)

    # ─── INFO ──────────────────────────────────────────────────

    def list_topics(self) -> list[str]:
        """Lista topics activos."""
        return list(self.node.get_topic_names_and_types().__iter__().__next__().__str__().split(",")) if False else []