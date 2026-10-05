/**
 * Atribución SDK — Criptografía.
 *
 * Firma ECDSA secp256k1 con SHA-256.
 * Compatible con el core Python.
 */

import { secp256k1 } from "@noble/curves/secp256k1";
import { sha256 } from "@noble/hashes/sha256";
import { sha3_256 } from "@noble/hashes/sha3";

/**
 * Serializa a JSON determinístico (claves ordenadas).
 */
export function canonicalJson(data: unknown): string {
  return JSON.stringify(data, Object.keys(data as object).sort());
}

export function canonicalBytes(data: unknown): Uint8Array {
  return new TextEncoder().encode(canonicalJson(data));
}

/**
 * Firma un payload con una clave privada hex.
 */
export function signPayload(privateKeyHex: string, payload: unknown): string {
  const priv = privateKeyHex.startsWith("0x")
    ? privateKeyHex.slice(2)
    : privateKeyHex;

  const msgHash = sha256(canonicalBytes(payload));
  const signature = secp256k1.sign(msgHash, priv);

  return "0x" + signature.toCompactHex();
}

/**
 * Verifica una firma contra una clave pública hex.
 */
export function verifySignature(
  publicKeyHex: string,
  payload: unknown,
  signatureHex: string
): boolean {
  try {
    const pub = publicKeyHex.startsWith("0x")
      ? publicKeyHex.slice(2)
      : publicKeyHex;
    const sig = signatureHex.startsWith("0x")
      ? signatureHex.slice(2)
      : signatureHex;

    const msgHash = sha256(canonicalBytes(payload));
    return secp256k1.verify(sig, msgHash, pub);
  } catch {
    return false;
  }
}

/**
 * Placeholder para firma post-cuántica.
 *
 * Cuando `@noble/post-quantum` esté disponible, se reemplaza
 * por ML-DSA real.
 */
export function signHybridPqcPlaceholder(payload: unknown): string {
  const h = sha3_256(canonicalBytes(payload));
  return "0x" + Buffer.from(h).toString("hex");
}