# TECH-DEBT — Atribución

> Registro honesto de deuda técnica y decisiones pendientes.
> Actualizar al cierre de cada bloque.
> Última revisión: 2026-10-06

---

## 🔴 CRÍTICO — Decisiones arquitectónicas (bloquean avance)

### TD-001: SafetyController no está cableado a actuadores
**Bloque:** Robotics (`robotics/actuation/safety.py`)
**Problema:** `trigger_emergency()` cambia el estado y loguea, pero
NO detiene motores ni servos. Es la capa de seguridad y no cumple
su función.
**Impacto:** En un robot físico, esto significa que detecta una
colisión pero sigue avanzando. Riesgo de daño físico.
**Decisión pendiente:** Definir mecanismo de integración. Opciones:
  - Hooks inyectados en `__init__` (`emergency_hooks=[motors.stop_all]`)
  - Event bus interno
  - Referencia directa a MotorController + ServoController
**Prioridad:** Antes de cualquier prueba con hardware real.
**Estimado:** 2-4h (diseño + implementación + test)

### TD-002: `robotics/` sin tests
**Bloque:** Robotics
**Problema:** No existe `robotics/tests/`. Ninguno de los 9 archivos
tiene cobertura.
**Impacto:** Los bugs de safety, motors, perception no se detectan
hasta que fallan en hardware.
**Plan:** Crear `robotics/tests/` con al menos:
  - `test_safety.py`: emergencia dispara hooks, reset funciona
  - `test_motors.py`: límites de velocidad, giro simétrico
  - `test_perception.py`: LiDAR clustering, visión con fixtures
**Prioridad:** Antes de integrar con hardware real.
**Estimado:** 1-2 días.

### TD-003: `robotics/` aislado del resto del sistema
**Bloque:** Robotics
**Problema:** No se integra con `core/` (¿el robot tiene DID?),
`guards/` (¿se auditan sus acciones?), ni `contracts/`
(¿se certifican sus operaciones on-chain?).
**Impacto:** Los robots son ciudadanos de segunda clase en Atribución.
No pueden certificarse KAF.
**Decisión pendiente:** Definir si un robot es un "agente" con
certificado KAF o una entidad separada. Documentar en ADR.
**Prioridad:** Antes de comercializar robotics.
**Estimado:** 4h (decisión + diseño).

---

## 🟠 ALTO — Bugs conocidos con impacto funcional

### TD-004: PaymentSplitter — underflow potencial
**Bloque:** Contracts (`contracts/PaymentSplitter.sol`)
**Problema:** `payment = (totalReceived * shares) / totalShares - released[account]`
puede revertir por underflow cuando el redondeo de Solidity deja
`released > calculado`.
**Impacto:** El último payee puede quedar sin poder retirar.
**Fix:** Usar `if (payment > 0)` en lugar de `require(payment != 0)`,
o proteger el cálculo con `max(0, ...)`.
**Prioridad:** Antes del primer deploy a Mainnet.
**Estimado:** 30 min + test.

### TD-005: `ros2.py` — `list_topics()` siempre devuelve `[]`
**Bloque:** Robotics (`robotics/drivers/ros2.py`)
**Problema:** Código muerto disfrazado:
`return list(...) if False else []`.
**Fix:** `return [name for name, _ in self.node.get_topic_names_and_types()]`
**Prioridad:** Media (no rompe nada, pero es mentira).
**Estimado:** 5 min.

### TD-006: `mqtt.py` — Firma de callbacks incompatible con paho-mqtt 2.x
**Bloque:** Robotics (`robotics/drivers/mqtt.py`)
**Problema:** Los callbacks `_on_connect` usan la firma vieja
(paho 1.x). Con paho 2.x los callbacks no se ejecutan.
**Impacto:** Un `pip install paho-mqtt` hoy instala 2.x y todo
falla silenciosamente.
**Fix:** Actualizar firma a `(client, userdata, flags, reason_code, properties=None)`
y pinnear `paho-mqtt>=2.0` en requirements.
**Prioridad:** Alta (rompe en instalación limpia).
**Estimado:** 15 min.

### TD-007: `mqtt.py` — `connect()` no espera conexión
**Bloque:** Robotics
**Problema:** `connect()` es asíncrono. Un `publish()` inmediato
después se pierde.
**Fix:** `wait_for_connect()` con threading.Event.
**Prioridad:** Alta.
**Estimado:** 20 min.

### TD-008: `safety.py` — No hay polling desde motores
**Bloque:** Robotics
**Problema:** `MotorController` nunca consulta `safety.is_safe_to_move()`.
**Fix:** Integrar con TD-001.
**Prioridad:** Alta (parte de TD-001).

---

## 🟡 MEDIO — Calidad y rendimiento

### TD-009: `vision.py` — Haar cascade recargado en cada llamada
**Bloque:** Robotics (`robotics/perception/vision.py`)
**Problema:** `cv2.CascadeClassifier(cascade_path)` dentro de
`detect_faces()`. Hace la función ~50x más lenta.
**Fix:** Cargar en `__init__`, guardar como `self._cascade`.
**Prioridad:** Media.
**Estimado:** 5 min.

### TD-010: `audio.py` — `detect_volume()` matemáticamente incorrecto
**Bloque:** Robotics (`robotics/perception/audio.py`)
**Problema:** Trata int16 como si fueran bytes centrados en 128.
Devuelve valores sin sentido.
**Fix:** Usar numpy correctamente:
```python
arr = np.frombuffer(audio_bytes, dtype='int16')
return min(1.0, float(np.abs(arr).mean()) / 32768.0)