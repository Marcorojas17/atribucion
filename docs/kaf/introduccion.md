# KAF — Introducción

**Kronos Assurance Framework.**

---

## ¿Qué es KAF?

KAF es un estándar de certificación de agentes IA.
Complementa y unifica:

- ISO 42001 (Sistema de Gestión de IA)
- ISO 27001 (Seguridad de la Información)
- SOC 2 Type II (Controles operativos)
- NIST AI RMF (Gestión de riesgos de IA)
- NOM-151-SCFI-2016 (Conservación de mensajes, México)
- EU AI Act (Reglamento UE 2024/1689)

---

## ¿Por qué existe?

ISO, SOC 2 y PCI DSS comparten ~80% de los controles.
KAF los unifica en un marco ejecutable por API.

**Ventaja:** el cliente no contrata 4 auditorías. Contrata una.

---

## Los 4 niveles

| Nivel | Nombre | Audiencia | Costo |
|---|---|---|---|
| **KAF-1** | Verified | Startups | Incluido en Free |
| **KAF-2** | Compliant | Scaleups EU | Incluido en Pro |
| **KAF-3** | Assured | Enterprise | €4.900 + €1.900/año |
| **KAF-4** | Sovereign | Bancos/Gobiernos | €19.900/año |

---

## Los 13 dominios

1. Identidad
2. Atribución
3. Trazabilidad
4. Supervisión
5. Explicabilidad
6. Seguridad
7. Privacidad
8. Continuidad
9. Criptografía
10. Pagos
11. Legal México
12. Gobernanza
13. (Reservado)

---

## Total: 47 controles

Cada dominio tiene entre 3 y 5 controles específicos.
Cada control es auditable automáticamente o requiere evidencia.

---

## Cómo empezar

1. Registra un agente en `api.atribucion.io/v1/agents`.
2. Ejecuta la auditoría: `POST /v1/kaf/assess/{agent_id}`.
3. Recibe tu nivel: KAF-1, KAF-2, KAF-3 o KAF-4.
4. Descarga el certificado verificable.

```bash
curl -X POST https://api.atribucion.io/v1/kaf/assess/agt_abc123 \
  -H "Authorization: Bearer $API_KEY"