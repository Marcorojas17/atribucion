```markdown
# Pagos en MXN y MXNB

---

## Por qué MXN

Atribución acepta pagos en pesos mexicanos por:

1. **Comodidad local.** El 80% de nuestros clientes iniciales son mexicanos.
2. **Menor fricción.** Evitamos conversión EUR → MXN.
3. **Compliance local.** El SAT requiere facturas en MXN.
4. **Estable.** El peso mexicano es la moneda de nuestra jurisdicción.

---

## Tipos de cambio

### Oráculo Banxico

```python
from payments.mxn.oracle import get_eur_mxn_rate

rate = await get_eur_mxn_rate()
# → 20.1 (actualizado cada 6h)
```

Fuente: Banxico API (serie SF43718).
Cache: 6 horas.
Fallback: 20.1 fijo si falla.

Configurar Banxico

1. Regístrate en banxico.org.mx.
2. Obtén token gratuito.
3. Añade a .env:

```env
BANXICO_TOKEN=tu_token
```

---

Conversión

```python
from payments.mxn.conversion import eur_to_mxn, mxn_to_eur

mxn = await eur_to_mxn(990)  # €990 → $19.899 MXN
eur = await mxn_to_eur(19900)  # $19.900 MXN → €990
```

---

Precios en MXN

Plan EUR MXN
Free €0 $0
Pro €990 $19.900
Bank €9.900 $199.000

---

MXNB — Stablecoin de Bitso

MXNB es una stablecoin regulada de Bitso, anclada 1:1
al peso mexicano. Aprobada por CNBV.

Por qué MXNB

1. 1:1 con MXN. Sin conversión.
2. Regulada. Reconocida por CNBV.
3. Blockchain. Transferencias en segundos.
4. Bajo costo. Comisiones mínimas.

Configurar

```env
BITSO_API_KEY=tu_key
BITSO_API_SECRET=tu_secret
```

Uso

```python
from payments.mxn.stablecoin import MXNBService

async with MXNBService() as service:
    balance = await service.get_balance()
    await service.send(
        to_address="rXXX...",
        amount_mxnb=19900,
        note="Pago plan Pro",
    )
```

Red

MXNB opera en XRPL (XRP Ledger):

· Transacciones en 3-5 segundos.
· Costo: <$0.01 USD.
· Dirección formato: rXXX...

---

Facturación CFDI

Para clientes mexicanos, Atribución emite CFDI 4.0:

· Uso: G03 (Gastos en general).
· Régimen: 601 (General de Ley Personas Morales).
· Método: PUE (Pago en una sola exhibición).
· Forma: 03 (Transferencia) o 04 (Tarjeta de crédito).

Descargar CFDI

```bash
curl https://api.atribucion.io/v1/invoices/{invoice_id}/cfdi \
  -H "Authorization: Bearer $API_KEY" \
  -o factura.xml
```

---

Comparativa de métodos

Método Moneda Costo Velocidad Compliance
Mercado Pago MXN MXN 3.49% Instantáneo ✅ SAT
SPEI MXN 0.99% <1 hora ✅ SAT
MXNB MXNB <0.1% <5 seg ✅ CNBV
Transferencia EUR EUR 0.5% 1-2 días ✅ EU

Recomendación: MXNB para pagos recurrentes.

---

Roadmap

Fase Mes Acción
1 1-3 Mercado Pago MXN
2 4-6 MXNB integrado
3 7-12 SPEI directo
4 13+ CBDC Banxico (cuando salga)

---

Recursos

· Banxico API
· Bitso MXNB
· XRPL
· SAT CFDI 4.0

```