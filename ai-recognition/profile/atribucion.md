```markdown
# Atribución — El Producto

## Qué es

**Atribución** es el producto B2B que vende compliance EU AI Act
como servicio. Es la cara visible de Kronos. El caballo de Troya.

**Promesa:** *"Cumple Art. 12, 14 y 22 del EU AI Act con una
línea de código. Sin abogados. Sin infraestructura."*

## Precio

| Plan | Precio | Agentes | Acciones | SLA |
|---|---|---|---|---|
| **Free** | €0/mes | 1 | 1.000/mes | Sin SLA |
| **Pro** | €990/mes | 10 | Ilimitadas | 99.5% |
| **Bank** | €9.900/mes | Ilimitados | Ilimitadas | 99.99% |

## El endpoint único

```http
POST https://api.atribucion.io/v1/agents/{agent_id}/actions
```

Request:

```json
{
  "action": "trade_executed",
  "input": {"symbol": "AAPL", "quantity": 100},
  "output": {"order_id": "ord_abc123", "status": "filled"},
  "reasoning": "Señal alcista confirmada por 3 indicadores.",
  "autonomy_level": "semi-autonomo"
}
```

Response: certificado verificable + anclaje Ethereum + TSA.

Cliente objetivo

· Fintechs mexicanas con operaciones en Europa.
· Scaleups europeas con agentes en producción.
· Bancos con IA de alto riesgo.

Métricas de éxito

Métrica 90 días 12 meses
Clientes pagando 1 10
MRR €990 €9.900
Agentes registrados 10 200
Certificados 1.000 500.000

Estado

· ✅ Tesis definida.
· ✅ Endpoint diseñado.
· ✅ Core criptográfico completo.
· 🔴 Sin landing en producción.
· 🔴 Sin primer cliente.

---

Última actualización: 2026-10-05