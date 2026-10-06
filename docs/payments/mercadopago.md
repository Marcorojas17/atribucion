```markdown
# Pagos con Mercado Pago

---

## Configuración

1. Crea cuenta en [mercadopago.com.mx](https://www.mercadopago.com.mx).
2. Ve a **Tus aplicaciones** → **Crear aplicación**.
3. Copia el **Access Token** (producción o test).
4. Añade a `.env`:

```env
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...
MERCADOPAGO_WEBHOOK_SECRET=tu_secret
```

---

Checkout Pro

Crear preferencia

```bash
curl -X POST https://api.atribucion.io/v1/payments/checkout \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "plan_id": "pro",
    "customer_email": "cliente@empresa.com",
    "back_url_success": "https://atribucion.io/checkout?status=success",
    "back_url_failure": "https://atribucion.io/checkout?status=failure",
    "back_url_pending": "https://atribucion.io/checkout?status=pending"
  }'
```

Respuesta:

```json
{
  "preference_id": "1234567890",
  "checkout_url": "https://www.mercadopago.com.mx/checkout/...",
  "sandbox_url": "https://sandbox.mercadopago.com.mx/checkout/..."
}
```

Redirigir al cliente

```html
<a href="https://www.mercadopago.com.mx/checkout/...">
  Pagar con Mercado Pago
</a>
```

---

Webhooks

Configurar

En el panel de Mercado Pago → Webhooks:

```
URL: https://api.atribucion.io/v1/payments/webhook
Eventos: payment, preapproval
```

Validar firma

Mercado Pago envía:

```http
x-signature: ts=1696449600,v1=<hmac_sha256>
x-request-id: <uuid>
```

Manifest a firmar:

```
id:<data_id>;request-id:<x_request_id>;ts:<ts>;
```

Código:

```python
from payments.mercadopago.verify import verify_webhook_signature

is_valid = verify_webhook_signature(
    x_signature=x_signature,
    x_request_id=x_request_id,
    data_id=data_id,
)
```

---

Suscripciones

Crear suscripción

```python
from payments.mercadopago.subscriptions import SubscriptionService
from payments.mercadopago.client import MercadoPagoClientBase

async with MercadoPagoClientBase() as client:
    service = SubscriptionService(client)
    sub = await service.create(
        reason="Atribución — Plan Pro",
        amount=19900,
        currency="MXN",
        frequency_months=1,
        customer_email="cliente@empresa.com",
        back_url="https://atribucion.io/checkout",
        external_reference="tnt_abc:pro",
    )
    print(sub.init_point)
```

---

Estados de pago

Estado MP Nuestro estado Acción
approved approved Activar plan
pending pending Esperar
in_process pending Esperar
rejected rejected Notificar cliente
refunded refunded Desactivar plan
cancelled cancelled Desactivar plan

---

Tarifas

Método Tarifa MP
Tarjeta crédito (1 cuota) 3.49% + $4 MXN
Tarjeta crédito (3 cuotas) 5.99%
Tarjeta débito 2.99%
Transferencia SPEI 0.99%
Efectivo (OXXO) 3.99%

Ejemplo: Pago Pro €990 (≈$19.900 MXN)

· Tarjeta 1 cuota: $699 MXN de comisión
· Neto: $19.201 MXN

---

Errores comunes

Error Causa Solución
invalid_access_token Token mal copiado Regenerar en panel
invalid_webhook_signature Secret incorrecto Verificar .env
preference_already_created Duplicado Usar external_reference único
payment_rejected Tarjeta rechazada Notificar al cliente

---

Recursos

· Docs oficiales
· Panel de aplicaciones
· Sandbox

```