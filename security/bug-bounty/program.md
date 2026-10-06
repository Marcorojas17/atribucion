# Bug Bounty Program

**Última actualización:** 2026-10-06
**Estado:** 🟡 Próximamente (mes 6)
**Plataforma:** HackerOne o Bugcrowd

---

## Objetivo

Recompensar a hackers éticos que encuentren vulnerabilidades
en Atribución antes de que sean explotadas.

---

## Rango de recompensas

| Severidad | CVSS | Recompensa | Ejemplos |
|---|---|---|---|
| **Crítica** | 9.0-10.0 | $5.000 | RCE, robo de claves, bypass auth |
| **Alta** | 7.0-8.9 | $1.500 | SQLi, SSRF crítico, IDOR |
| **Media** | 4.0-6.9 | $500 | XSS almacenado, CSRF |
| **Baja** | 0.1-3.9 | $100 | XSS reflejado, info disclosure menor |
| **Informativa** | 0.0 | Crédito | Mejoras, sin vulnerabilidad |

**Máximo por reporte:** $5.000
**Máximo por investigador/año:** $25.000

---

## Proceso de reporte

### 1. Envío
- Plataforma: HackerOne (preferido) o bugcrowd
- Formato: título, severidad, pasos, PoC, impacto
- Cifrado: PGP opcional para reportes sensibles

### 2. Confirmación (24h)
- Recibimos el reporte.
- Confirmamos recepción.
- Asignamos ID de caso.

### 3. Triaje (72h)
- Evaluamos severidad real.
- Validamos reproducible.
- Notificamos al investigador.

### 4. Fix (7-30 días)
- Desarrollamos el parche.
- Desplegamos a staging.
- Verificamos que soluciona.

### 5. Recompensa (15 días post-fix)
- Pagamos vía transferencia bancaria o cripto.
- Publicamos crédito (si autoriza).
- Cerramos caso.

---

## Reglas de participación

### ✅ Permitido
- Reportar vulnerabilidades en scope.
- Usar PoC mínimos.
- Coordinar divulgación con nosotros.
- Múltiples reportes del mismo investigador.

### ❌ Prohibido
- Dañar el sistema o datos.
- Acceder a datos de otros usuarios.
- Realizar DoS/DDoS.
- Ingeniería social a empleados.
- Ataques físicos.
- Spam o auto-promoción.
- Reportar vulnerabilidades de terceros sin contexto.

---

## Fuera de scope

- **Dominios:** no listados en scope.
- **Tipos:** mejoras de performance, missing headers sin impacto.
- **Reportes duplicados:** primera recepción válida gana.
- **Vulnerabilidades conocidas:** dependencias con CVE público.
- **Self-XSS:** que requiera user interaction manual.
- **Missing rate limiting:** sin exploit demostrable.
- **Bugs de UI/UX:** sin impacto de seguridad.

---

## Divulgación

### Coordinada
- Por defecto: 90 días desde fix.
- Extensible por acuerdo mutuo.
- Publicamos post-mortem.

### Inmediata
- Solo si la vulnerabilidad ya es pública.
- Solo si hay riesgo activo para usuarios.
- Solo con notificación previa al investigador.

### Nunca
- Detalles técnicos explotables antes del fix.
- Información personal del investigador sin permiso.

---

## Reconocimiento

### Hall of Fame
Publicamos (con permiso) en:
```text
atribucion.io/security/hall-of-fame

Severidad Rango base Bonus por calidad
Crítica $5.000 +$1.000 si incluye fix sugerido
Alta $1.500 +$300 si incluye PoC automatizado
Media $500 +$100 si incluye test de regresión
Baja $100 —

Mes Presupuesto Cobertura
6-9 $2.000 Reportes iniciales
10-12 $5.000 Activo con plataforma
13-18 $10.000 Escalado
19+ $15.000 Continuo

Plataforma Costo Ventajas Desventajas
HackerOne 20% del bounty Mayor comunidad Más caro
Bugcrowd 20% del bounty Buena UI Menos hackers
Intigriti 15% del bounty Europa Menor comunidad
YesWeHack 15% del bounty Europa —
Self-hosted 0% Control total Menor visibilidad



Métrica Objetivo año 1
Reportes válidos 10
Reportes críticos 1
Tiempo medio de triaje <72h
Tiempo medio de fix <30d
Tiempo medio de pago <15d post-fix
Reputación del programa Top 50% en plataforma

