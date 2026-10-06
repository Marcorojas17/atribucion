```markdown
# NOM-151-SCFI-2016 — Mapping

**Norma Oficial Mexicana para conservación de mensajes de datos.**

---

## Aplicabilidad

**Obligatoria** para cualquier entidad que digitalice o
conserve documentos con efectos legales en México.

Atribución aplica porque:
- Emite certificados con efectos legales.
- Conserva mensajes de datos (acciones de agentes).
- Requiere validez probatoria ante tribunales mexicanos.

---

## Requisitos NOM-151

### 1. Integridad del mensaje

**Exige:** el mensaje debe conservarse sin alteraciones desde
su generación.

**Atribución cumple:**
- ✅ Hash SHA-256 al momento de creación.
- ✅ Firma ECDSA + ML-DSA.
- ✅ Anclaje a Ethereum.
- ✅ Append-only log.

**Implementación:**
- `core/src/atribucion/crypto.py::hash_double`
- `core/src/atribucion/merkle.py`
- `core/src/atribucion/anchor.py`

---

### 2. Constancia de conservación

**Exige:** documento que acredite:
- Fecha/hora de generación
- Fecha/hora de conservación
- Identidad del prestador
- Algoritmo utilizado

**Atribución cumple:**
- ✅ Se genera constancia NOM-151 con cada certificado.
- ✅ Se firma con clave híbrida.
- ✅ Se sella con PSC acreditado.
- ✅ Se archiva en IPFS + Arweave.

**Implementación:**
- `payments/nom151/constancia.py`
- `payments/nom151/sello.py`

**Estado:** 🟡 Integración con PSC pendiente.

---

### 3. Sello de tiempo

**Exige:** sello emitido por Prestador de Servicios de
Certificación (PSC) acreditado por la Secretaría de Economía.

**Atribución cumple:**
- ✅ Sello RFC 3161 interno (DigiCert).
- 🟡 Sello PSC (Mifiel/Incode) — integración pendiente.

**Implementación:**
- `core/src/atribucion/tsa.py`
- `payments/nom151/psc_client.py`

**Estado:** 🟡 Integración pendiente. Roadmap mes 3-6.

---

### 4. Firma electrónica avanzada

**Exige:** firma que cumpla con la Ley de Firma Electrónica
Avanzada.

**Atribución cumple:**
- ✅ Firma ECDSA secp256k1.
- ✅ Firma ML-DSA (post-cuántico).
- ✅ Certificados de firma vigentes.
- ✅ Validación de cadena.

**Implementación:**
- `core/src/atribucion/crypto.py::sign_hybrid`
- `core/src/atribucion/crypto.py::verify_hybrid`

---

### 5. Conservación mínima

**Exige:** 5 años mínimo (algunos casos 10).

**Atribución cumple:**
- ✅ IPFS (permanente).
- ✅ Arweave (permanente).
- ✅ Ethereum (permanente).
- ✅ Logs (365 días rotados, hash chain).

**Implementación:**
- `core/src/atribucion/anchor.py::pin_to_ipfs`
- `core/src/atribucion/anchor.py::_real_anchor`

---

## PSC seleccionado

**Preferido:** Mifiel
- API moderna
- Costo accesible ($0.05-0.20/firma)
- Enfoque legal
- Integración simple

**Alternativa:** Incode
- Más grande
- API robusta
- Costo mayor

---

## Roadmap

| Fase | Mes | Acción |
|---|---|---|
| 1 | 1-2 | Investigar PSC + cotizar |
| 2 | 3-4 | Integrar con Mifiel |
| 3 | 5-6 | Testing con documentos reales |
| 4 | 7-9 | Auditoría legal de validez |
| 5 | 10+ | Acreditación propia (opcional) |

---

## Costos

| Concepto | Costo |
|---|---|
| Integración PSC | 2-4 semanas de desarrollo |
| Costo por sello | $0.05-0.20 USD |
| Costo mensual (1.000 sellos) | $50-200 USD |
| Auditoría legal | €5.000-10.000 |
| Acreditación propia (año 2+) | €120.000 |

---

## Por qué importa

Sin NOM-151:
- ❌ Certificados sin validez legal en México
- ❌ Imposible vender a fintechs mexicanas
- ❌ Imposible vender a gobierno
- ❌ Imposible vender a bancos

Con NOM-151:
- ✅ Validez probatoria ante tribunales
- ✅ Aceptable por CNBV
- ✅ Aceptable por SAT
- ✅ Diferenciador vs. competencia

---

## Referencias

- NOM-151-SCFI-2016 (DOF 30/06/2016)
- Ley de Firma Electrónica Avanzada
- Código de Comercio (Arts. 89-114)
- Lista de PSCs: [gob.mx/se](https://www.gob.mx/se)
- Mifiel: [mifiel.com](https://www.mifiel.com)
- Incode: [incode.com](https://incode.com)
```
