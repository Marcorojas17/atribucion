# Anti-patrones prohibidos

**Lo que una IA NO debe hacer en este proyecto.**

---

## En código

- ❌ "Sería bueno considerar..." → propón o cállate.
- ❌ Duplicar conceptos (agentes x2, bóveda x3).
- ❌ Carpetas numeradas mezcladas con semánticas.
- ❌ HTML/JS/PY sueltos en la raíz.
- ❌ Más de 6 workflows en `.github/`.
- ❌ Claims sin código que los respalde.
- ❌ Reinventar crypto, DID, VCs, timestamping.
- ❌ Ignorar post-cuántico, legal o robots.
- ❌ TODOs sin issue asociado.

## En respuestas

- ❌ "¡Excelente pregunta!"
- ❌ "Sería bueno considerar..."
- ❌ "Podrías intentar..."
- ❌ "Es importante notar que..."
- ❌ Dar teoría sin código.
- ❌ Pedir contexto ya provisto.
- ❌ Generar 20 archivos de golpe.
- ❌ Cambiar de tema sin cerrar.

## En arquitectura

- ❌ Proponer microservicios cuando no hay equipo.
- ❌ Proponer Kubernetes cuando no hay tráfico.
- ❌ Proponer multi-región cuando hay 1 cliente.
- ❌ Proponer blockchain propia cuando Ethereum basta.
- ❌ Proponer token especulativo.
- ❌ Proponer features sin cliente esperando.

## En proceso

- ❌ Reiniciar desde cero si hay contexto previo.
- ❌ Ignorar `AI-CONTEXT.md` y `AGENTS.md`.
- ❌ No marcar deuda con 🔴.
- ❌ No marcar logros con 🟢.
- ❌ No cerrar sesión con pendientes claros.

---

## Cómo reemplazar cada anti-patrón

| Anti-patrón | Reemplazo |
|---|---|
| "Sería bueno considerar..." | "Propongo X porque Y. Aquí está el código." |
| "Podrías intentar..." | "Haz esto: [comando exacto]." |
| Dar teoría sin código | Dar código + explicación breve. |
| Pedir contexto ya provisto | Leer los archivos primero. |
| Generar 20 archivos | 4-5 por tanda, confirmar entre tandas. |
| Proponer Kubernetes | Docker Compose hasta 100 clientes. |
| Proponer token | KRN respaldado por contribución, no especulativo. |

---

## Excepción

Si crees que un anti-patrón debe romperse por razón técnica
válida, **pregunta primero**. No lo rompas por tu cuenta.

---

**Última actualización:** 2026-10-05