```markdown
<div align="center">

# Atribución

**Compliance EU AI Act para agentes IA en un solo endpoint.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-en%20construcci%C3%B3n-orange.svg)](#estado)

</div>

---

## 📖 Tabla de contenidos

- [El problema](#-el-problema)
- [La solución](#-la-solución)
- [Cómo funciona](#-cómo-funciona)
- [Estado](#-estado)
- [Estructura](#-estructura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Licencias](#-licencias)
- [Autor](#-autor)

---

## 🎯 El problema

Desde agosto de 2026, el **EU AI Act** obliga a toda empresa
que despliegue agentes IA de alto riesgo a:

| Artículo | Exige | Multa por incumplir |
|---|---|---|
| **Art. 12** | Registro automático de eventos | Hasta €35M o 7% facturación |
| **Art. 14** | Supervisión humana efectiva | Hasta €35M o 7% facturación |
| **Art. 22** | Explicabilidad de decisiones | Hasta €35M o 7% facturación |

El 90% de las empresas europeas con agentes en producción
**no está preparada**. Contratar abogados cuesta €50.000+
y no resuelve el problema técnico: ¿cómo pruebas que cada
acción de tu agente ocurrió, cuándo y con qué razonamiento?

---

## 💡 La solución

**Un endpoint. Una línea de código.**

```bash
curl -X POST https://api.atribucion.io/v1/agents/{agent_id}/actions \
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
```

Recibes:

· Un certificado verificable (W3C VC 2.0).
· Un anclaje en Ethereum (inmutable, público).
· Un sello de tiempo RFC 3161 (reconocido por eIDAS 2.0).
· Un informe mensual PDF listo para auditores.

Cumples Art. 12, 14 y 22. Sin abogados. Sin infraestructura.

---

⚙️ Cómo funciona

```text
┌─────────────────────────────────────────────────────────┐
│  TU AGENTE IA                                           │
│  (Codex, Claude, GPT, Gemini, local...)                 │
└────────────────────┬────────────────────────────────────┘
                     │  POST /v1/agents/{id}/actions
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ATRIBUCIÓN API                                         │
│                                                         │
│  1. Verifica firma híbrida (ECDSA + ML-DSA)             │
│  2. Valida contra Contrato de Atribución                │
│  3. Emite credencial verificable (VC 2.0)               │
│  4. Ancla Merkle root a Ethereum                        │
│  5. Sella con TSA (RFC 3161)                            │
│  6. Registra para auditoría                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  CERTIFICADO + PRUEBA CRIPTOGRÁFICA                     │
│  - verificable por cualquiera                           │
│  - permanente (Ethereum + Arweave)                      │
│  - reconocido legalmente (eIDAS, NOM-151)               │
└─────────────────────────────────────────────────────────┘
```

Post-cuántico desde el día 1: cada firma usa ECDSA
(clásica) + ML-DSA (Dilithium, resistente a cuántico).
Verificación válida solo si ambas pasan.

---

📊 Estado

🚧 En construcción — fase fundacional.

✅ Funciona y está probado

☑ Firmas híbridas ECDSA + ML-DSA
☑ Serialización canónica JSON
☑ Hashing doble SHA-256 + SHA-3
☑ Identidad descentralizada (DID W3C)
☑ Contrato de Atribución con validación
☑ Credenciales verificables (VC 2.0)
☑ Merkle trees para anclaje eficiente
☑ Anclaje a Ethereum (modo mock funcional)
☑ Sellado de tiempo RFC 3161 (modo mock funcional)

🔴 En desarrollo

☐ Endpoint API público
☐ SDK Python + JavaScript
☐ Landing pública
☐ Dashboard para clientes
☐ Primer cliente piloto

---

🗂️ Estructura

```text
atribucion/
│
├── README.md
├── LICENSE-MIT
├── LICENSE-APACHE
├── requirements.txt
├── .gitignore
├── .env.example
│
├── core/                          # Protocolo criptográfico
│   └── src/
│       └── atribucion/
│           ├── crypto.py          # Firmas híbridas ECDSA + ML-DSA
│           ├── did.py             # Identidad W3C
│           ├── contract.py        # Contrato de Atribución
│           ├── vc.py              # Credenciales verificables
│           ├── merkle.py          # Anclaje eficiente
│           ├── anchor.py          # Ethereum (mock/real)
│           └── tsa.py             # Sellado RFC 3161
│
├── api/                           # (en desarrollo)
├── sdk/                           # (en desarrollo)
└── tests/                         # (en desarrollo)
```

---

🚀 Instalación

Requisitos

· Python 3.11+
· pip
· Git

Setup

```bash
# Clonar
git clone https://github.com/Marcorojas17/atribucion.git
cd atribucion

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

---

💻 Uso

Ejemplo: firmar una acción

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

# Emitir credencial de una acción
cred = vc.issue(
    credential_id="cert_001",
    issuer=agent_did,
    subject=agent_did,
    action={"action": "trade", "input": {}, "output": {}},
    evidence={"ipfs_cid": "bafy...", "sha256": "..."},
)

# Firmar
cred = vc.attach_proof(cred, priv)

# Verificar
assert vc.verify(cred, pub)
print("✅ Credencial válida")
```

---

📄 Licencias

Componente Licencia
Código (core, sdk) MIT + Apache 2.0
Especificación CC-BY 4.0
Marca "Atribución" Trademark

Puedes: usar, modificar, distribuir, uso comercial.
Debes: mantener el aviso de copyright.
No puedes: usar la marca "Atribución" para certificar
sin permiso.

---

👤 Autor

Marco Antonio Rojas Valdivín

Fundador de Atribución y Kronos Protocol.

Construyendo desde México, con la tesis de que la próxima
década necesita infraestructura legal para agentes autónomos
—y que esa infraestructura debe ser criptográfica, no territorial.

· GitHub: @Marcorojas17
· Repo: atribucion

---

<div align="center">

Atribución no compite con Microsoft, Google, OpenAI ni Anthropic.
Construye la capa que todas ellas necesitarán adoptar.

</div>
```