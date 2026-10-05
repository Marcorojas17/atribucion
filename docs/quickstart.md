```markdown
# Quickstart

**Integra Atribución en 5 minutos.**

---

## 1. Obtén tu API key

Regístrate en [atribucion.io](https://atribucion.io).

Recibirás una API key con formato:

```text
ak_live_<64_hex>
```

Guárdala en un lugar seguro. Solo se muestra una vez.

---

2. Registra tu agente

```bash
curl -X POST https://api.atribucion.io/v1/agents \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MiAgenteTrading",
    "autonomy_level": "semi-autonomo",
    "proveedor_modelo": "anthropic",
    "operator_did": "did:kronos:human:0x..."
  }'
```

Respuesta:

```json
{
  "agent_id": "agt_abc123",
  "agent_did": "did:kronos:agent:0x...",
  "contract_id": "ctr_xyz789",
  "api_key": "ak_live_..."
}
```

Guarda el agent_id. Lo usarás en cada llamada.

---

3. Firma cada acción

Cada vez que tu agente actúe, envía la acción a Atribución.

Python

```python
import httpx
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# 1. Cargar tu clave privada
with open("agent_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# 2. Construir la acción
action = {
    "action": "trade_executed",
    "input": {"symbol": "AAPL", "quantity": 100},
    "output": {"order_id": "ord_1", "status": "filled"},
    "reasoning": "Señal alcista confirmada por 3 indicadores.",
    "autonomy_level": "semi-autonomo",
}

# 3. Firmar (canonical JSON → bytes → ECDSA)
payload = json.dumps(action, sort_keys=True, separators=(",", ":")).encode()
sig_classic = "0x" + private_key.sign(payload, ec.ECDSA(hashes.SHA256())).hex()
sig_pqc = "0x" + "0" * 128  # placeholder hasta integrar ML-DSA

# 4. Enviar
response = httpx.post(
    f"https://api.atribucion.io/v1/agents/{AGENT_ID}/actions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "X-Agent-Signature": sig_classic,
        "X-Agent-Signature-PQC": sig_pqc,
    },
    json=action,
)

certificate = response.json()
print("Certificado:", certificate["certificate_id"])
print("Prueba:", certificate["proof_url"])
```

JavaScript / TypeScript

```typescript
import { sign } from "crypto";

const action = {
  action: "trade_executed",
  input: { symbol: "AAPL", quantity: 100 },
  output: { order_id: "ord_1", status: "filled" },
  reasoning: "Señal alcista confirmada.",
  autonomy_level: "semi-autonomo",
};

const payload = JSON.stringify(action, Object.keys(action).sort());

const signature = sign("sha256", Buffer.from(payload), privateKey)
  .toString("hex");

const response = await fetch(
  `https://api.atribucion.io/v1/agents/${AGENT_ID}/actions`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "X-Agent-Signature": `0x${signature}`,
      "X-Agent-Signature-PQC": `0x${"0".repeat(128)}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(action),
  }
);

const certificate = await response.json();
console.log("Certificado:", certificate.certificate_id);
```

---

4. Verifica el certificado

Cualquiera puede verificar un certificado sin permiso:

```bash
curl https://api.atribucion.io/v1/proofs/cert_abc123
```

O abre directamente:

```text
https://atribucion.io/verify/cert_abc123
```

---

5. Descarga tu informe mensual

El día 1 de cada mes, tendrás disponible:

```bash
curl https://api.atribucion.io/v1/reports/2026-10 \
  -H "Authorization: Bearer $API_KEY" \
  -o informe-octubre.pdf
```

El PDF incluye:

· Total de acciones registradas.
· Cumplimiento Art. 12, 14, 22.
· Pruebas criptográficas (hashes, anclajes, sellos).
· Listo para entregar a auditores.

---

Errores comunes

Código Significado Solución
401 API key inválida Verifica el header Authorization
401 Firma inválida Verifica que firmas el JSON canónico
404 Agente no encontrado Verifica el agent_id
422 Violación del contrato Verifica autonomy_level y reasoning
429 Rate limit excedido Espera 1 minuto

---

Soporte

· Docs: docs.atribucion.io
· Email: marco.a.rojas.v@hotmail.com
· GitHub: github.com/Marcorojas17/atribucion

```
