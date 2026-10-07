<div align="center">

# Atribución

**Compliance EU AI Act para agentes IA en un solo endpoint.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/Marcorojas17/atribucion/actions/workflows/ci.yml/badge.svg)](https://github.com/Marcorojas17/atribucion/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/status-live-brightgreen.svg)](#estado)

</div>

---

## 🎯 El problema

Desde agosto de 2026, el **EU AI Act** obliga a toda empresa que despliegue agentes IA de alto riesgo a:

| Artículo | Exige | Multa |
|---|---|---|
| **Art. 12** | Registro automático de eventos | Hasta €35M o 7% facturación |
| **Art. 14** | Supervisión humana efectiva | Hasta €35M o 7% facturación |
| **Art. 22** | Explicabilidad de decisiones | Hasta €35M o 7% facturación |

El 90% de las empresas europeas con agentes en producción **no está preparada**.

---

## 💡 La solución

**Un endpoint. Una línea de código.**

```bash
curl -X POST https://atribucion-api.onrender.com/v1/agents/{agent_id}/actions \
  -H "Authorization: Bearer $API_KEY" \
  -H "X-Agent-Signature: 0x..." \
  -H "X-Agent-Signature-PQC: 0x..." \
  -H "Content-Type: application/json" \
  -d '{
    "action": "trade_executed",
    "input": {"symbol": "AAPL", "quantity": 100},
    "output": {"order_id": "ord_abc123", "status": "filled"},
    "reasoning": "Señal alcista confirmada por 3 indicadores.",
    "autonomy_level": "semi-autonomo"
  }'

Recibes:

· Un certificado verificable (W3C VC 2.0).
· Un anclaje en Ethereum (inmutable, público).
· Un sello de tiempo RFC 3161 (reconocido por eIDAS 2.0).
· Un informe mensual PDF listo para auditores.

Post-cuántico desde el día 1: cada firma usa ECDSA + ML-DSA. Verificación válida solo si ambas pasan.

---

🚀 API en vivo

Endpoint URL
API pública https://atribucion-api.onrender.com
Documentación https://atribucion-api.onrender.com/docs
Health check https://atribucion-api.onrender.com/v1/health
Landing https://marcorojas17.github.io/atribucion/
Verificador https://marcorojas17.github.io/atribucion/verifier/

---

📊 Estado

Fase: MVP funcional en producción.

✅ Funciona y está probado

· Firmas híbridas ECDSA + ML-DSA
· Serialización canónica JSON
· Hashing doble SHA-256 + SHA-3
· Identidad descentralizada (DID W3C)
· Contrato de Atribución con validación
· Credenciales verificables (VC 2.0)
· Merkle trees para anclaje eficiente
· Anclaje a Ethereum (mock funcional)
· Sellado de tiempo RFC 3161 (mock funcional)
· API pública en producción (Render, Docker)
· 101 tests pasando
· CI verde en GitHub Actions
· SDK Python + SDK JavaScript
· Landing pública + verificador
· 9 guardianes autónomos (SHA, ACTA, TSA, PHOENIX, NEXUS, VAULT, MRR, ORACLE, SENTINEL)
· Engine + MADRE (orquestador multi-agente)
· KAF (estándar de certificación, 4 niveles)

🔴 Próximos pasos

· Conectar dominio propio (atribucion.io)
· Primer cliente piloto
· Auditoría externa (ISO 27001, SOC 2)

---

🗂️ Estructura

```text
atribucion/
├── core/            # Protocolo criptográfico
├── api/             # Endpoints FastAPI
├── atribucion/      # Lógica de negocio (billing, onboarding)
├── engine/          # Motor de agentes + MADRE
├── guards/          # 9 guardianes autónomos
├── mesh/            # Malla P2P
├── kaf/             # Estándar de certificación
├── robotics/        # Interfaz con hardware
├── sdk/             # SDKs (Python + JavaScript)
├── apps/            # Frontend estático
├── contracts/       # Solidity (Ethereum)
├── docs/            # Documentación
├── security/        # Políticas y compliance
├── legal/           # Términos y privacidad
├── ai-recognition/  # Contexto para IA (MCP)
└── tests/           # Suite de tests
```

---

🚀 Instalación

```bash
git clone https://github.com/Marcorojas17/atribucion.git
cd atribucion

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

---

💻 Uso

```python
import sys
sys.path.insert(0, "core/src")

from atribucion import crypto, did, contract, vc

# Crear identidad del agente
agent_did = did.create("kronos", "agent", {"name": "MiAgente"})

# Generar claves
priv, pub = crypto.generate_ecdsa_keypair()

# Crear contrato
contrato = contract.create_default(
    agent_did=agent_did,
    creator_did="did:kronos:human:0x...",
    operator_did="did:kronos:human:0x...",
    autonomy_level="semi-autonomo",
    proveedor_modelo="anthropic",
)

# Emitir y firmar credencial
cred = vc.issue(
    credential_id="cert_001",
    issuer=agent_did,
    subject=agent_did,
    action={"action": "trade", "input": {}, "output": {}},
    evidence={"ipfs_cid": "bafy...", "sha256": "..."},
)
cred = vc.attach_proof(cred, priv)

assert vc.verify(cred, pub)
print("✅ Credencial válida")
```

---

📄 Licencias

Componente Licencia
Código (core, sdk) MIT + Apache 2.0
Especificación CC-BY 4.0
Marca "Atribución" Trademark

---

👤 Autor

Marco Antonio Rojas Valdovinos

Fundador de Atribución y Kronos Protocol.

GitHub: @Marcorojas17

---

<div align="center">

Atribución no compite con Microsoft, Google, OpenAI ni Anthropic.

Construye la capa que todas ellas necesitarán adoptar.

</div>
```