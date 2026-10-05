# Decisiones arquitectónicas

**Architecture Decision Records (ADR).**

---

## ADR-001 — Kronos es protocolo, no jurisdicción completa

**Fecha:** 2026-10-04
**Estado:** Aceptada

**Contexto:** Kronos aspira a ser jurisdicción digital, pero
arrancar como jurisdicción completa requiere 5+ años y equipo.

**Decisión:** Empezar como protocolo con SDK. La jurisdicción
se construye encima, a medida que haya clientes.

**Consecuencia:** El foco inmediato es `spec/` + `sdk/` +
`apps/`. Lo demás es soporte.

---

## ADR-002 — Producto = Atribución (caballo de Troya)

**Fecha:** 2026-10-04
**Estado:** Aceptada

**Contexto:** Necesitamos vender algo concreto ya.

**Decisión:** El producto visible es Atribución (compliance
EU AI Act). Kronos se cuela por debajo.

**Consecuencia:** El endpoint es `POST /v1/agents/{id}/actions`.
El cliente cree que compra compliance. Adopta Kronos sin saberlo.

---

## ADR-003 — Firmas híbridas desde el día 1

**Fecha:** 2026-10-04
**Estado:** Aceptada

**Contexto:** NIST fijó 2035 para migración post-cuántica.

**Decisión:** Todas las firmas son ECDSA + ML-DSA desde hoy.

**Consecuencia:** No hay deuda técnica post-cuántica. Es un
argumento de venta brutal.

---

## ADR-004 — No depender de AWS

**Fecha:** 2026-10-04
**Estado:** Aceptada

**Contexto:** AWS es caro y centralizado.

**Decisión:** Todo corre en Railway (dev) + GitHub Pages (frontend).

**Consecuencia:** Costo de infra < €50/mes hasta 100 clientes.

---

## ADR-005 — Consolidar duplicaciones

**Fecha:** 2026-10-05
**Estado:** Aceptada

**Contexto:** Había `legal/LICENSE-*` duplicando raíz,
`core/tests/` duplicando `tests/`.

**Decisión:** Un concepto → una ubicación. Sin excepciones.

**Consecuencia:** Eliminar duplicados. Mantener solo la
ubicación canónica.

---

**Última actualización:** 2026-10-05