
```markdown
# Referencia del API

**Base URL:** `https://api.atribucion.io`

**Versión:** v1

---

## Autenticación

Todos los endpoints (excepto `/v1/proofs/*` y `/v1/health`) requieren:

```http
Authorization: Bearer ak_live_<64_hex>
```

---

Endpoints

1. Healthcheck

```http
GET /v1/health
```

Sin auth. Devuelve el estado del servicio.

Respuesta:

```json
{
  "status": "ok",
  "service": "atribucion-api",
  "version": "0.1.0",
  "timestamp": "2026-10-04T22:00:00Z"
}
```

---

2. Registrar agente

```http
POST /v1/agents
```

Body:

```json
{
  "name": "MiAgenteTrading",
  "autonomy_level": "semi-autonomo",
  "proveedor_modelo": "anthropic",
  "operator_did": "did:kronos:human:0x...",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
  "metadata": {}
}
```

Respuesta 201:

```json
{
  "agent_id": "agt_abc123",
  "agent_did": "did:kronos:agent:0x...",
  "contract_id": "ctr_xyz789",
  "contract_url": "https://api.atribucion.io/v1/contracts/ctr_xyz789",
  "created_at": "2026-10-04T22:00:00Z",
  "autonomy_level": "semi-autonomo",
  "colateral_krn": 2000,
  "limite_dano_krn": 10000
}
```

---

3. Registrar acción

```http
POST /v1/agents/{agent_id}/actions
```

Headers obligatorios:

· Authorization: Bearer <api_key>
· X-Agent-Signature: 0x... (firma ECDSA hex)
· X-Agent-Signature-PQC: 0x... (firma PQC hex)

Body:

```json
{
  "action": "trade_executed",
  "input": {"symbol": "AAPL", "quantity": 100},
  "output": {"order_id": "ord_1", "status": "filled"},
  "reasoning": "Señal alcista confirmada.",
  "autonomy_level": "semi-autonomo",
  "human_approval": null
}
```

Respuesta 201:

```json
{
  "certificate_id": "cert_abc123",
  "proof_url": "https://api.atribucion.io/v1/proofs/cert_abc123",
  "compliance": {
    "eu_ai_act": {
      "article_12": "compliant",
      "article_14": "not_applicable",
      "article_22": "compliant"
    }
  },
  "anchor": {
    "tx_hash": "0x...",
    "block": 0,
    "network": "mock",
    "merkle_root": "0x..."
  },
  "timestamp_rfc3161": {
    "authority": "mock-tsa",
    "sealed_at": "2026-10-04T22:00:00Z",
    "token": "0x..."
  },
  "signature": {
    "classic": "0x...",
    "pqc": "0x..."
  }
}
```

Errores:

Código Causa
401 API key o firma inválida
404 Agente no encontrado
422 Violación del Contrato de Atribución

---

4. Obtener agente

```http
GET /v1/agents/{agent_id}
```

Respuesta 200:

```json
{
  "agent_id": "agt_abc123",
  "agent_did": "did:kronos:agent:0x...",
  "name": "MiAgente",
  "autonomy_level": "semi-autonomo",
  "proveedor_modelo": "anthropic",
  "created_at": "2026-10-04T22:00:00Z",
  "active": true
}
```

---

5. Verificar certificado

```http
GET /v1/proofs/{certificate_id}
```

Sin auth. Cualquiera puede verificar.

Respuesta 200:

```json
{
  "certificate_id": "cert_abc123",
  "status": "válido",
  "issued_at": "2026-10-04T22:00:00Z",
  "agent_did": "did:kronos:agent:0x...",
  "action": "action_recorded",
  "autonomy_level": "semi-autonomo",
  "hashes": {
    "sha256": "abc...",
    "sha3": "def..."
  },
  "anchor": {
    "tx_hash": "0x...",
    "network": "mock",
    "merkle_root": "0x..."
  },
  "timestamp": {
    "authority": "mock-tsa",
    "sealed_at": "2026-10-04T22:00:00Z",
    "token": "0x..."
  },
  "verification_url": "https://atribucion.io/verify/cert_abc123"
}
```

---

6. Crear checkout

```http
POST /v1/payments/checkout
```

Body:

```json
{
  "plan_id": "pro",
  "customer_email": "cliente@empresa.com",
  "back_url_success": "https://atribucion.io/checkout?status=success",
  "back_url_failure": "https://atribucion.io/checkout?status=failure",
  "back_url_pending": "https://atribucion.io/checkout?status=pending"
}
```

Respuesta 201:

```json
{
  "preference_id": "1234567890",
  "checkout_url": "https://www.mercadopago.com.mx/checkout/v1/redirect?...",
  "sandbox_url": "https://sandbox.mercadopago.com.mx/checkout/v1/redirect?..."
}
```

---

7. Estado de suscripción

```http
GET /v1/payments/status
```

Respuesta 200:

```json
{
  "preapproval_id": "abc123",
  "tenant_id": "tnt_xyz",
  "plan_id": "pro",
  "status": "active",
  "next_payment_date": "2026-11-04T22:00:00Z",
  "amount_mxn": 19900.0
}
```

---

8. Informe mensual (JSON)

```http
GET /v1/reports/{yyyy-mm}
```

Respuesta 200:

```json
{
  "period": "2026-10",
  "tenant_id": "tnt_xyz",
  "generated_at": "2026-11-01T00:00:00Z",
  "summary": {
    "total_actions": 1523,
    "total_agents": 3,
    "total_certificates": 1523
  },
  "compliance": {
    "eu_ai_act": {
      "article_12": "compliant",
      "article_14": "compliant",
      "article_22": "compliant"
    }
  },
  "proofs": {
    "merkle_root": "0x...",
    "anchor_tx": "0x...",
    "anchor_network": "polygon",
    "tsa_authority": "DigiCert"
  }
}
```

---

9. Informe mensual (PDF)

```http
GET /v1/reports/{yyyy-mm}.pdf
```

Respuesta 200: application/pdf

---

Códigos de estado

Código Significado
200 OK
201 Creado
400 Bad Request
401 No autorizado
404 No encontrado
422 Validación fallida
429 Rate limit excedido
500 Error interno
502 Error en servicio externo

---

Rate limiting

· Free: 100 req/min
· Pro: 1.000 req/min
· Bank: 10.000 req/min

Headers de respuesta:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997
X-RateLimit-Reset: 1696449600
```

---

Webhooks

Pago confirmado

```http
POST https://tu-servidor.com/webhook
```

Body:

```json
{
  "type": "payment",
  "action": "payment.created",
  "data": {
    "id": "1234567890"
  }
}
```

Validación:

El webhook incluye headers que debes validar:

```http
x-signature: ts=1696449600,v1=<hash_hmac_sha256>
x-request-id: <uuid>
```

Manifest a firmar:

```text
id:<data_id>;request-id:<x_request_id>;ts:<ts>;
```

---

SDKs oficiales

· Python: pip install atribucion-sdk
· JavaScript: npm install @atribucion/sdk

---

Soporte

· Docs: docs.atribucion.io
· Email: marco.a.rojas.v@hotmail.com
· GitHub: github.com/Marcorojas17/atribucion

```