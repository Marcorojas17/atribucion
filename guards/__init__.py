"""Los 9 guardianes de Atribución."""

from guards.acta.agent import ACTAGuard
from guards.base import Finding, GuardAgent
from guards.mrr.agent import MRRGuard
from guards.nexus.agent import NexusGuard
from guards.oracle.agent import OracleGuard
from guards.phoenix.agent import PhoenixGuard
from guards.sentinel.agent import SentinelGuard
from guards.sha.agent import SHAGuard
from guards.tsa.agent import TSAGuard
from guards.vault.agent import VaultGuard

ALL_GUARDS = [
    SHAGuard,
    ACTAGuard,
    TSAGuard,
    PhoenixGuard,
    NexusGuard,
    VaultGuard,
    MRRGuard,
    OracleGuard,
    SentinelGuard,
]

__all__ = [
    "Finding",
    "GuardAgent",
    "ALL_GUARDS",
    "ACTAGuard",
    "MRRGuard",
    "NexusGuard",
    "OracleGuard",
    "PhoenixGuard",
    "SentinelGuard",
    "SHAGuard",
    "TSAGuard",
    "VaultGuard",
]