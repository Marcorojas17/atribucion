# Seguridad

**Atribución — nivel bancario.**

---

## Documentación

| Documento | Descripción |
|---|---|
| [ISO 27001](../../security/compliance/iso-27001.md) | Compliance ISO 27001 |
| [SOC 2 Type II](../../security/compliance/soc2-type2.md) | Compliance SOC 2 |
| [PCI DSS](../../security/compliance/pci-dss.md) | Compliance PCI DSS |
| [NIST 800-57](../../security/compliance/nist-800-57.md) | Gestión de claves |
| [NOM-151](../../security/compliance/nom-151.md) | Compliance México |

## Políticas

| Política | Descripción |
|---|---|
| [Access Control](../../security/policies/access-control.md) | Zero Trust + RBAC |
| [Encryption](../../security/policies/encryption.md) | TLS 1.3 + AES-256 + PQC |
| [Incident Response](../../security/policies/incident-response.md) | 5 niveles SEV |
| [Key Rotation](../../security/policies/key-rotation.md) | Ciclo de rotación |

## Auditorías

- [Internas](../../security/audits/internal/README.md) — Trimestrales
- [Externas](../../security/audits/external/README.md) — Anuales

## Bug Bounty

- [Programa](../../security/bug-bounty/program.md)
- [Scope](../../security/bug-bounty/scope.md)

---

## Reportar vulnerabilidad

**NO abras un issue público.**

Email: **security@atribucion.io**
Asunto: `[SECURITY] Descripción breve`

Incluye:
1. Descripción del problema.
2. Pasos para reproducir.
3. Impacto potencial.
4. Versión afectada.
5. Sugerencia de fix (opcional).

**Respuesta:** 24 horas.

---

## Estado de certificaciones

| Certificación | Estado | Fecha |
|---|---|---|
| ISO 27001 | 🔴 En roadmap | Mes 7-12 |
| SOC 2 Type I | 🔴 En roadmap | Mes 4-6 |
| SOC 2 Type II | 🔴 En roadmap | Mes 10-12 |
| ISO 42001 | 🔴 En roadmap | Mes 13-18 |
| NOM-151 | 🟡 En integración | Mes 3-6 |
| Bug Bounty | 🟡 Próximamente | Mes 6 |
| Pentesting | 🔴 En roadmap | Mes 4-6 |

---

## Stack de seguridad

- **Criptografía:** ECDSA + ML-DSA + AES-256-GCM + TLS 1.3
- **Identidad:** W3C DID + VC 2.0 + mTLS
- **Aplicación:** Pydantic validation + rate limiting + audit logs
- **Infraestructura:** Docker non-root + Vault (roadmap)
- **Blockchain:** Ethereum + multi-sig + timelock

---

## Contacto

- **Security:** security@atribucion.io
- **Bug bounty:** security@atribucion.io
- **Status:** status.atribucion.io