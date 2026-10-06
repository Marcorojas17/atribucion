```markdown
# KAF — Certificación

---

## Flujo completo

### 1. Registro del agente

```bash
curl -X POST https://api.atribucion.io/v1/agents \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "name": "MiAgente",
    "autonomy_level": "semi-autonomo",
    "proveedor_modelo": "anthropic",
    "operator_did": "did:kronos:human:0x...",
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\n..."
  }'
```

2. Auditoría automática

```bash
curl -X POST https://api.atribucion.io/v1/kaf/assess/agt_abc123 \
  -H "Authorization: Bearer $API_KEY"
```

Respuesta:

```json
{
  "agent_id": "agt_abc123",
  "level_achieved": "KAF-2",
  "controls_passed": 15,
  "controls_total": 47,
  "timestamp": "2026-10-06T00:00:00Z"
}
```

3. Emisión de certificado

Se emite automáticamente si el nivel es ≥ KAF-1.

Formato:

· ID: kaf_<hex>
· Firmado con clave híbrida.
· Anclado a Ethereum.
· Publicado en registro público.

4. Verificación pública

```bash
curl https://api.atribucion.io/v1/kaf/verify/kaf_abc123
```

Cualquiera puede verificar sin autenticación.

---

Renovación

Nivel Validez Re-auditoría
KAF-1 12 meses Automática
KAF-2 12 meses Automática
KAF-3 12 meses Manual (externa)
KAF-4 12 meses Manual (Big Four)

---

Revocación

Un certificado puede revocarse si:

· El agente viola el Contrato de Atribución.
· Se detecta fraude en la evidencia.
· El creador lo solicita.
· El Tribunal Kronos lo ordena.

Proceso:

1. Notificación al titular.
2. Período de gracia de 30 días.
3. Publicación en registro público.
4. Reembolso parcial (si aplica).

---

API de certificación

Endpoint Método Descripción
/v1/kaf/assess/{agent_id} POST Auditoría
/v1/kaf/verify/{cert_id} GET Verificación pública
/v1/kaf/levels GET Listar niveles

---

Costos

Nivel Auditoría Anual
KAF-1 €0 €0
KAF-2 €0 Incluido en Pro
KAF-3 €4.900 €1.900
KAF-4 Incluido €19.900

---

Roadmap de adopción

Año Objetivo
2026 100 agentes KAF-1 + 20 KAF-2
2027 1.000 KAF-2 + 50 KAF-3 + 5 KAF-4
2028 10.000 KAF-2 + 500 KAF-3 + 50 KAF-4
2029+ KAF como estándar de facto

```