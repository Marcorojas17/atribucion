/**
 * Atribución SDK — Entry point.
 */

export { AtribucionClient } from "./client.js";
export {
  canonicalJson,
  canonicalBytes,
  signPayload,
  verifySignature,
  signHybridPqcPlaceholder,
} from "./crypto.js";

export type {
  ActionResponse,
  AgentInfo,
  AgentRegistrationResponse,
  AutonomyLevel,
  ClientOptions,
  HumanApproval,
  ProofResponse,
  ProveedorModelo,
  RecordActionInput,
  RegisterAgentInput,
} from "./types.js";

export const VERSION = "0.1.0";