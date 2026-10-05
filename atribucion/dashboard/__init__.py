"""Dashboard y persistencia de Atribución."""

from atribucion.dashboard.repository import (
    AgentRepository,
    CertificateRepository,
    TenantRepository,
)

__all__ = ["AgentRepository", "CertificateRepository", "TenantRepository"]