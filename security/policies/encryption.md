# Encryption Policy

**Última actualización:** 2026-10-06
**Versión:** 1.0.0
**Owner:** Marco Antonio Rojas Valdovinos

---

## 1. Principio rector

**Todo cifrado por defecto.** Ningún dato sensible viaja
o reposa sin cifrado. Sin excepciones.

## 2. Algoritmos aprobados

### 2.1 Firma digital
| Algoritmo | Uso | Estándar |
|---|---|---|
| ECDSA secp256k1 | Clásica | SEC 2 |
| Ed25519 | Alternativa | RFC 8032 |
| ML-DSA-65 (Dilithium3) | Post-cuántica | NIST FIPS 204 |
| SLH-DSA (SPHINCS+) | Respaldo PQC | NIST FIPS 205 |

### 2.2 Hash
| Algoritmo | Uso |
|---|---|
| SHA-256 | Principal |
| SHA3-256 | Complementario |
| BLAKE3 | Verificación rápida |

### 2.3 Cifrado simétrico
| Algoritmo | Uso |
|---|---|
| AES-256-GCM | Datos en reposo |
| ChaCha20-Poly1305 | Alternativa en móvil |

### 2.4 Intercambio de claves
| Algoritmo | Uso |
|---|---|
| X25519 | Clásico |
| ML-KEM-768 (Kyber768) | Post-cuántico |
| Híbrido | Producción |

### 2.5 Transporte
| Protocolo | Uso |
|---|---|
| TLS 1.3 | Obligatorio |
| TLS 1.2 | Solo con justificación |
| QUIC | Para P2P |

## 3. Cifrado en tránsito

### 3.1 API pública
- **TLS 1.3 obligatorio.**
- HSTS con `max-age=31536000; includeSubDomains; preload`.
- Cipher suites recomendadas:
  - `TLS_AES_256_GCM_SHA384`
  - `TLS_CHACHA20_POLY1305_SHA256`
  - `TLS_AES_128_GCM_SHA256`

### 3.2 Servicio a servicio
- **mTLS obligatorio.**
- Certificados rotados cada 90 días.
- CA interna (Vault PKI, roadmap).

### 3.3 Cliente → API
- HTTPS obligatorio.
- HTTP solo en localhost para desarrollo.
- Certificate pinning en apps móviles.

## 4. Cifrado en reposo

### 4.1 Bases de datos
- **AES-256-GCM** para todo dato sensible.
- **Claves en HSM** (roadmap).
- **Rotación de claves:** cada 90 días.

### 4.2 Backups
- Cifrados con **clave separada** del sistema principal.
- Almacenados en ubicación geográfica distinta.
- Verificación de restauración: mensual.

### 4.3 Archivos temporales
- Cifrados con clave efímera.
- Eliminados en 24h.
- Nunca contienen datos de producción.

### 4.4 Logs
- **Datos sensibles redactados** antes de persistir.
- Logs cifrados en reposo.
- Retención según política.

## 5. Cifrado de datos específicos

| Tipo de dato | Cifrado | Notas |
|---|---|---|
| Claves privadas | HSM | Nunca salen del dispositivo |
| Contraseñas | Argon2id | Hash + salt |
| API keys | SHA-256 | Solo hash almacenado |
| Datos personales | AES-256-GCM | Cifrado en app |
| Certificados | Firma + hash | Inmutables |
| Contratos | Firma + hash | Inmutables |
| Mensajes | AES-256-GCM | Cifrado extremo a extremo |

## 6. Gestión de claves

### 6.1 Generación
- Fuente: entropía del sistema operativo.
- Validación matemática post-generación.
- Nunca generadas en entornos compartidos.

### 6.2 Almacenamiento
- **HSM** para claves de producción.
- **Memory-safe** para claves de uso temporal.
- **Nunca** en código fuente, logs o git.

### 6.3 Distribución
- Claves públicas: publicación abierta (DID Document).
- Claves privadas: nunca se distribuyen.
- Claves simétricas: TLS 1.3 o KMS.

### 6.4 Rotación
- **Claves de firma:** cada 90 días.
- **Claves de cifrado:** cada 90 días.
- **TLS:** cada 90 días (Let's Encrypt).
- **Backups:** cada 12 meses.

### 6.5 Destrucción
- Sobrescritura + eliminación segura.
- Registro de destrucción.
- Rotación de claves derivadas.

## 7. Post-cuántico

### 7.1 Estado actual
- **Firmas:** ECDSA + ML-DSA (híbridas desde día 1).
- **Cifrado:** X25519 + ML-KEM (roadmap).
- **Hash:** SHA-256 + SHA3-256 (doble).

### 7.2 Roadmap
| Fase | Mes | Acción |
|---|---|---|
| 1 | 1-3 | Firmas híbridas activas |
| 2 | 4-6 | Cifrado híbrido activo |
| 3 | 7-12 | Auditoría PQC externa |
| 4 | 13+ | Migración completa |

## 8. Verificación de cumplimiento

### 8.1 Checklist mensual
- [ ] TLS 1.3 en todos los endpoints
- [ ] Certificados vigentes (>30 días)
- [ ] Rotación de claves al día
- [ ] Logs cifrados y redactados
- [ ] Backups cifrados y verificados

### 8.2 Auditoría anual
- Revisión de algoritmos usados.
- Verificación de HSM.
- Pruebas de penetración.
- Revisión de políticas.

## 9. Referencias

- NIST SP 800-57 (Key Management)
- NIST SP 800-52 Rev 2 (TLS)
- NIST FIPS 203 (ML-KEM)
- NIST FIPS 204 (ML-DSA)
- NIST FIPS 205 (SLH-DSA)
- OWASP Cryptographic Storage Cheat Sheet
- ISO 27001 A.10 (Cryptography)