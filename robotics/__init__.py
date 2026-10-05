"""
Atribución — Robotics.

Interfaz con hardware físico.

Módulos:
    drivers    → ROS2, MQTT, Modbus
    identity   → hardware_id (TPM), DID del robot, proof-of-presence
    perception → vision, lidar, audio
    actuation  → motors, servos, safety

Filosofía: cada robot es un ciudadano Kronos con DID,
proof-of-physical-presence y contrato de atribución.
"""

__version__ = "0.1.0"