```markdown
# EU AI Act — Mapping

**Reglamento (UE) 2024/1689.**

---

## Aplicabilidad

Atribución **no es** un sistema de IA de alto riesgo.
Es **infraestructura de compliance** para sistemas de IA.

Sin embargo, Atribución cumple con EU AI Act para:
1. Dar ejemplo.
2. Permitir a sus clientes cumplir.
3. Prepararse para futuras regulaciones.

---

## Artículos aplicables a Atribución

### Art. 12 — Registro de eventos

**Exige:** registrar automáticamente eventos durante toda
la vida útil del sistema.

**Atribución cumple:**
- ✅ Cada acción se registra en log inmutable.
- ✅ Se firma con ECDSA + ML-DSA.
- ✅ Se ancla a Ethereum.
- ✅ Retención ≥ 10 años.

**Implementación:**
- `api/middleware/audit.py`
- `core/src/atribucion/anchor.py`
- `guards/acta/agent.py`

---

### Art. 14 — Supervisión humana

**Exige:** supervisión humana efectiva.

**Atribución cumple:**
- ✅ Nivel `supervisado` requiere aprobación humana firmada.
- ✅ Dashboard con panel de control.
- ✅ Kill switch en dashboard.
- ✅ Alertas automáticas.

**Implementación:**
- `api/schemas/action.py::HumanApproval`
- `api/routes/actions.py`
- `guards/phoenix/agent.py`

---

### Art. 22 — Decisión automatizada

**Exige:** derecho a explicación de decisiones automatizadas.

**Atribución cumple:**
- ✅ Nivel `autonomo` requiere `reasoning`.
- ✅ Reasoning se hashea y ancla.
- ✅ Endpoint público de explicación.
- ✅ Retención ≥ 10 años.

**Implementación:**
- `api/schemas/action.py::ActionRequest`
- `core/src/atribucion/vc.py`
- `api/routes/actions.py`

---

## Artículos NO aplicables

### Art. 5 — Prácticas prohibidas
Atribución no realiza manipulación, scraping masivo, etc.

### Art. 6 — Clasificación de alto riesgo
Atribución no es un sistema de IA de alto riesgo.

### Art. 9-15 — Requisitos de alto riesgo
No aplica si no es alto riesgo.

### Art. 16-27 — Obligaciones de proveedores
Atribución no es proveedor de modelo fundacional.

### Art. 50 — Transparencia
Atribución declara ser infraestructura, no sistema de IA.

---

## Multi-jurisdicción

Atribución cumple con:

| Regulación | País/Región | Estado |
|---|---|---|
| EU AI Act | UE | ✅ Compliance por diseño |
| GDPR | UE | ✅ Compliance |
| LFPDPPP | México | ✅ Compliance |
| NOM-151 | México | 🟡 Integración |
| CNBV | México | 🟡 Mapeo |
| ISO 42001 | Global | 🔴 Roadmap |
| NIST AI RMF | USA | 🔴 Roadmap |

---

## Roadmap de compliance

| Mes | Hito |
|---|---|
| 1-3 | Documentar compliance EU AI Act |
| 4-6 | Auditoría interna |
| 7-12 | Certificación ISO 42001 |
| 13-18 | Auditoría externa |
| 19+ | Adopción por reguladores |

---

## Cómo ayuda a clientes

Atribución permite a clientes cumplir EU AI Act
sin contratar abogados:

| Artículo | Atribución ofrece |
|---|---|
| Art. 12 | Registro automático + anclaje |
| Art. 14 | Aprobación humana + alertas |
| Art. 22 | Reasoning documentado + endpoint |
| Art. 9 | Análisis de riesgos (roadmap) |
| Art. 10 | Gestión de datos (roadmap) |
| Art. 11 | Documentación técnica (roadmap) |
| Art. 13 | Transparencia (roadmap) |
| Art. 15 | Robustez (roadmap) |
| Art. 17 | Sistema de gestión (roadmap) |

**Roadmap:** cubrir los 9 artículos en 18 meses.

---

## Contacto

- **Compliance:** compliance@atribucion.io
- **Legal:** legal@atribucion.io
- **Docs:** [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
```
