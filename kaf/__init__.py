"""
Atribución — KAF (Kronos Assurance Framework).

Estándar propio de certificación de agentes IA.
Complementa ISO 42001, ISO 27001, SOC 2, NIST AI RMF y NOM-151
con controles específicos para agentes autónomos y preparación
post-cuántica.

4 niveles:
    KAF-1 Verified    → DID + firma + log
    KAF-2 Compliant   → KAF-1 + Contrato de Atribución + anclaje
    KAF-3 Assured     → KAF-2 + ISO 27001 + SOC 2 + HSM
    KAF-4 Sovereign   → KAF-3 + PQC + NOM-151 + tribunal

13 dominios de control:
    1. Identidad      8. Continuidad
    2. Atribución     9. Criptografía
    3. Trazabilidad  10. Pagos
    4. Supervisión   11. Legal MX
    5. Explicabilidad 12. Gobernanza
    6. Seguridad     13. (reservado)
    7. Privacidad
"""

__version__ = "1.0.0"