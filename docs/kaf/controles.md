# KAF — Controles

**47 controles en 13 dominios.**

---

## Dominio 1 — Identidad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-1.1 | DID registrado | Critical | ✅ |
| KAF-1.2 | VC vigente | Critical | ✅ |
| KAF-1.3 | Claves rotadas ≤90d | High | ✅ |
| KAF-1.4 | DID Document público | Medium | ✅ |

---

## Dominio 2 — Atribución

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-2.1 | Contrato firmado | Critical | ✅ |
| KAF-2.2 | Colateral depositado | Critical | ✅ |
| KAF-2.3 | Nivel autonomía declarado | High | ✅ |
| KAF-2.4 | Límite daño configurado | High | ✅ |

---

## Dominio 3 — Trazabilidad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-3.1 | Log inmutable | Critical | ✅ |
| KAF-3.2 | Firma por acción | Critical | ✅ |
| KAF-3.3 | Anclaje Ethereum ≤6h | Critical | ✅ |
| KAF-3.4 | Hash doble | High | ✅ |
| KAF-3.5 | IPFS archival | Medium | ✅ |

---

## Dominio 4 — Supervisión

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-4.1 | Aprobación humana documentada | Critical | ✅ |
| KAF-4.2 | Alertas automáticas | High | ✅ |
| KAF-4.3 | Kill switch | High | ❌ |

---

## Dominio 5 — Explicabilidad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-5.1 | Reasoning documentado | Critical | ✅ |
| KAF-5.2 | Razonamiento hasheado | High | ✅ |
| KAF-5.3 | Endpoint público explicación | Medium | ✅ |

---

## Dominio 6 — Seguridad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-6.1 | ISO 27001 vigente | Critical | ❌ |
| KAF-6.2 | SOC 2 Type II | High | ❌ |
| KAF-6.3 | Pentesting anual | High | ❌ |
| KAF-6.4 | HSM para claves | Critical | ❌ |
| KAF-6.5 | Zero Trust | High | ✅ |

---

## Dominio 7 — Privacidad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-7.1 | GDPR compliance | Critical | ❌ |
| KAF-7.2 | LFPDPPP compliance | High | ❌ |
| KAF-7.3 | Datos personales fuera de cadena | Critical | ✅ |
| KAF-7.4 | Cifrado en reposo AES-256 | High | ✅ |

---

## Dominio 8 — Continuidad

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-8.1 | Backups diarios ≥30d | High | ✅ |
| KAF-8.2 | DR plan probado | High | ❌ |
| KAF-8.3 | SLA ≥99.5% | Medium | ✅ |

---

## Dominio 9 — Criptografía

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-9.1 | Firmas híbridas ECDSA+ML-DSA | Critical | ✅ |
| KAF-9.2 | PQC completo | Critical | ✅ |
| KAF-9.3 | Rotación claves ≤90d | High | ✅ |
| KAF-9.4 | TLS 1.3 obligatorio | High | ✅ |

---

## Dominio 10 — Pagos

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-10.1 | PCI DSS v4.0 | High | ❌ |
| KAF-10.2 | No almacenamiento tarjeta | Critical | ✅ |
| KAF-10.3 | Webhooks firmados HMAC | High | ✅ |

---

## Dominio 11 — Legal México

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-11.1 | NOM-151 | High | ❌ |
| KAF-11.2 | PSC acreditado | High | ❌ |
| KAF-11.3 | Mapeo CNBV | Medium | ❌ |

---

## Dominio 12 — Gobernanza

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-12.1 | ISO 42001 | Critical | ❌ |
| KAF-12.2 | NIST AI RMF | High | ❌ |
| KAF-12.3 | Políticas documentadas | High | ❌ |
| KAF-12.4 | Auditoría anual externa | High | ❌ |

---

## Resumen

| Severidad | Total |
|---|---|
| Critical | 18 |
| High | 22 |
| Medium | 7 |
| **Total** | **47** |

| Auto-auditable | Total |
|---|---|
| ✅ Sí | 27 |
| ❌ No (requiere evidencia externa) | 20 |