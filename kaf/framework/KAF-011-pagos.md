# KAF-011 — Pagos

**Dominio 11 de 13.**

## Objetivo

Garantizar seguridad en procesamiento de pagos.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-10.1 | PCI DSS v4.0 | High | ❌ |
| KAF-10.2 | No almacenamiento de datos de tarjeta | Critical | ✅ |
| KAF-10.3 | Webhooks firmados (HMAC-SHA256) | High | ✅ |

## Requisitos

### PCI DSS v4.0

Si se procesan pagos con tarjeta directamente.
No aplica si se usa Mercado Pago/Stripe como intermediario.

### No almacenamiento

Los datos de tarjeta nunca se almacenan en servidores propios.
El procesamiento se delega a Mercado Pago.

### Webhooks firmados

Todo webhook de pago debe verificar:

```

x-signature: ts=<ts>,v1=<hmac_sha256>
x-request-id: <uuid>

Manifest a firmar: `id:<data_id>;request-id:<x_request_id>;ts:<ts>;`

## Integración con Mercado Pago

- Checkout Pro para pagos únicos
- Preapproval para suscripciones
- Validación HMAC de webhooks

## Evidencia

- Configuración de Mercado Pago
- Log de webhooks procesados
- Verificación de firmas
- Contrato con procesador de pagos