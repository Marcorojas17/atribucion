# KAF-2 — Compliant

**Nivel de compliance EU AI Act.**

---

## Requisitos

KAF-2 = KAF-1 + los siguientes controles:

| Control | Descripción |
|---|---|
| **KAF-2.1** | Contrato de Atribución firmado |
| **KAF-2.2** | Colateral depositado en escrow |
| **KAF-2.3** | Nivel de autonomía declarado |
| **KAF-2.4** | Límite de daño configurado |
| **KAF-3.3** | Anclaje a Ethereum cada ≤6h |
| **KAF-3.4** | Hash doble (SHA-256 + SHA-3) |
| **KAF-4.1** | Aprobación humana para acciones supervisadas |
| **KAF-5.1** | Reasoning documentado en acciones autónomas |
| **KAF-5.2** | Razonamiento hasheado y anclado |
| **KAF-7.3** | Datos personales fuera de cadena |

**Total: 15 controles acumulados.**

---

## Proceso

1. El agente ya tiene KAF-1.
2. Se firma el Contrato de Atribución (agente + creador + operador).
3. Se deposita colateral en escrow según nivel de autonomía.
4. Se ejecuta la auditoría automática de los 10 controles.
5. Si pasa, recibe KAF-2 (verificado por Atribución).

**Tiempo:** < 1 hora.
**Costo:** incluido en plan Pro (€990/mes).
**Válido por:** 12 meses.

---

## Qué certifica

- Cumplimiento con EU AI Act Art. 12, 14, 22.
- Contrato de Atribución legalmente firmado.
- Colateral y seguro de responsabilidad.
- Anclaje a Ethereum mainnet.
- Reasoning documentado y verificable.

**Cumple:** EU AI Act Art. 12, 14, 22.

---

## Dirigido a

- Scaleups europeas con agentes en producción.
- Fintechs con operaciones en la UE.
- Empresas que necesitan compliance para vender a la UE.

---

## Verificación

```bash
curl https://api.atribucion.io/v1/kaf/verify/{certificate_id}