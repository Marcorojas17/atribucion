# PCI DSS v4.0 — Compliance

## Estado

🟢 **No aplica directamente.**

Atribución **no procesa datos de tarjeta** directamente.
Usamos Mercado Pago como intermediario.

## Qué certifica

Payment Card Industry Data Security Standard.
Obligatorio para cualquier entidad que procese, almacene
o transmita datos de tarjetas de crédito.

## ¿Por qué no aplica?

Atribución delega el procesamiento de pagos a Mercado Pago.
El cliente es redirigido a la pasarela de Mercado Pago,
que sí cumple PCI DSS Nivel 1.

**Modelo:** SAQ A (Self-Assessment Questionnaire A)
- Merchant e-commerce que delega pagos a procesador PCI-compliant.
- No almacenamos datos de tarjeta.
- No procesamos datos de tarjeta.
- No transmitimos datos de tarjeta.

## SAQ A — Requisitos aplicables

Aunque no aplica PCI DSS completo, el SAQ A exige:

| Requisito | Estado |
|---|---|
| Redireccionamiento a pasarela PCI-compliant | ✅ |
| No almacenar datos de tarjeta | ✅ |
| No procesar datos de tarjeta | ✅ |
| Aceptar solo canales seguros (TLS 1.3) | ✅ |
| Mantener políticas de seguridad | ✅ |
| Gestión de incidentes | 🟡 |
| Capacitación anual de empleados | 🔴 |

## Si en el futuro procesamos pagos

Si Atribución decide integrar pagos directos:

1. **PCI DSS Nivel 4** (menos de 20.000 transacciones/año)
   - SAQ A-EP o SAQ D
   - Costo: €5.000-15.000

2. **PCI DSS Nivel 1** (más de 6M transacciones/año)
   - Auditoría por QSA certificado
   - Costo: €50.000-200.000/año

**Recomendación:** mantener el modelo de delegación
a Mercado Pago. Es más simple y más seguro.

## Datos de pago que SÍ manejamos

Atribución almacena:

- ✅ Últimos 4 dígitos de tarjeta (para mostrar al cliente)
- ✅ Nombre del titular (para facturación)
- ✅ Fecha de expiración (para mostrar al cliente)
- ❌ NUNCA el número completo
- ❌ NUNCA el CVV
- ❌ NUNCA datos de banda magnética

## Políticas de seguridad

- **Acceso:** solo empleados con necesidad de conocer
- **Cifrado:** AES-256-GCM para datos en reposo
- **Auditoría:** log inmutable de accesos
- **Retención:** 7 años (fiscal)
- **Eliminación:** segura al expirar

## Roadmap

| Fase | Mes | Acción |
|---|---|---|
| Actual | — | SAQ A (delegación a Mercado Pago) |
| Fase 2 | 12+ | Evaluar integración directa |
| Fase 3 | 18+ | Obtener SAQ A-EP |

## Referencias

- PCI DSS v4.0 (PCI Security Standards Council)
- SAQ A (Self-Assessment Questionnaire A)
- Mercado Pago PCI DSS Compliance