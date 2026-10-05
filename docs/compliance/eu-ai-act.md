
```markdown
# Cumplimiento EU AI Act con Atribución

**Cómo convertir una obligación regulatoria en una línea de código.**

---

## ¿Qué exige el EU AI Act?

El **Reglamento (UE) 2024/1689** entró en vigor el 1 de agosto de 2024.
Las obligaciones para sistemas de IA de alto riesgo aplican desde
**agosto de 2026**.

### Los 3 artículos que afectan a tu empresa

| Artículo | Exige | Multa por incumplir |
|---|---|---|
| **Art. 12** | Registro automático de eventos durante toda la vida útil del sistema | Hasta €35M o 7% facturación |
| **Art. 14** | Supervisión humana efectiva, con capacidad de intervención | Hasta €35M o 7% facturación |
| **Art. 22** | Derecho a explicación de decisiones automatizadas | Hasta €35M o 7% facturación |

### ¿A quién aplica?

A cualquier empresa que **despliegue en la UE** un sistema de IA
de alto riesgo. Incluye:

- Bots de trading y agentes financieros.
- Asistentes médicos con IA.
- Sistemas de RRHH que evalúan personas.
- Agentes de atención al cliente con impacto legal.
- Cualquier IA que afecte derechos fundamentales.

**No importa si la empresa es europea o no. Si el efecto ocurre
en la UE, aplica.**

---

## ¿Cómo lo resuelve Atribución?

### Art. 12 — Registro automático

**Lo que exige:** cada acción del sistema debe registrarse de forma
inalterable, con timestamp y trazabilidad.

**Lo que hace Atribución:**

```bash
curl -X POST https://api.atribucion.io/v1/agents/{id}/actions \
  -d '{"action": "trade_executed", ...}'
```

Cada llamada produce:

1. Una credencial verificable (W3C VC 2.0).
2. Un anclaje en Ethereum (inmutable, público).
3. Un hash doble (SHA-256 + SHA-3).
4. Un archivado en IPFS (permanente, 10+ años).

Resultado: el registro es inalterable por diseño. Ni tú, ni
tu equipo, ni un atacante pueden modificarlo.

Art. 14 — Supervisión humana

Lo que exige: un humano debe poder intervenir, y la intervención
debe ser verificable.

Lo que hace Atribución:

· Si declaras autonomy_level: supervisado, cada acción exige
  human_approval firmada por un DID humano.
· Si el humano no firma, el certificado no se emite.
· La firma humana se incluye en el certificado final.

Resultado: tienes prueba criptográfica de que un humano
supervisó cada acción crítica.

Art. 22 — Explicabilidad

Lo que exige: el usuario debe poder obtener una explicación
de las decisiones automatizadas que le afectan.

Lo que hace Atribución:

· Si declaras autonomy_level: autonomo, cada acción exige
  un campo reasoning con la justificación del agente.
· El reasoning se hashea, firma y ancla.
· Cualquiera puede verificar que la explicación existía
  en el momento de la decisión.

Resultado: la explicación no es opcional, no es retroactiva,
y no se puede cambiar.

---

Comparativa: hacerlo solo vs. con Atribución

Tarea Hacerlo solo Con Atribución
Log inmutable Implementar Merkle trees + anclaje blockchain 1 línea
Firma de cada acción Implementar ECDSA + gestión de claves 1 línea
Sellado de tiempo legal Contratar TSA + integrar RFC 3161 1 línea
Verificación pública Construir endpoint + UI 1 línea
Reportes para auditores Contratar abogados + generar PDFs 1 línea
Preparación post-cuántica Implementar ML-DSA + migración 1 línea
Tiempo estimado 6-12 meses 1 día
Costo estimado €80.000 - €200.000 €990/mes

---

¿Cómo se lo demuestras a un auditor?

Cada mes, Atribución te entrega un informe de cumplimiento PDF con:

1. Portada con tu nombre de empresa y período.
2. Resumen ejecutivo de acciones registradas.
3. Tabla de cumplimiento por artículo.
4. Pruebas criptográficas:
   · Merkle root del período.
   · TX hash del anclaje en Ethereum.
   · Sello de tiempo RFC 3161 (emitido por DigiCert).
5. Certificado de atestación firmado por Atribución.
6. Instrucciones de verificación para el auditor.

El auditor puede verificar cada punto sin contactar a Atribución.

---

¿Por qué esto no lo puede hacer cualquier empresa?

Porque requiere combinar seis tecnologías simultáneamente:

Tecnología Dificultad Tiempo
Criptografía post-cuántica Alta 6+ meses
Anclaje blockchain Media 2-3 meses
W3C DID + VC 2.0 Media 2-3 meses
RFC 3161 + TSA acreditada Alta 3-4 meses
Arquitectura Zero Trust Alta 4-6 meses
Cumplimiento legal multi-jurisdicción Muy alta 12+ meses

Atribución ya lo hizo. Tú solo usas el endpoint.

---

Riesgos si NO implementas nada

Si tu empresa despliega agentes IA en la UE sin cumplir con
Art. 12, 14 y 22:

1. Multas de hasta €35M o 7% de facturación global.
2. Suspensión del sistema por orden regulatoria.
3. Responsabilidad civil por daños causados.
4. Daño reputacional irrecuperable.
5. Imposibilidad de operar en la UE.

El costo de cumplir es menor que el costo de no cumplir.

---

Empezar

Crear cuenta →

· Free: 1 agente, 1.000 acciones/mes, sin costo.
· Pro: 10 agentes, ilimitado, €990/mes.
· Bank: agentes ilimitados, SLA 99.99%, €9.900/mes.

---

Recursos adicionales

· Texto oficial del EU AI Act
· Guía de implementación de la Comisión Europea
· W3C Verifiable Credentials 2.0
· RFC 3161 — Time-Stamp Protocol

---

Atribución no es asesoría legal. Es la infraestructura técnica
que hace posible cumplir con el EU AI Act. Para asesoría legal
específica, consulta a un abogado especializado.

```