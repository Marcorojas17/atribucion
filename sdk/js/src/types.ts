/**
 * Atribución SDK — Tipos públicos.
 */

// ─────────────────────────────────────────────────────────────
// INPUTS
// ─────────────────────────────────────────────────────────────

export type AutonomyLevel = "supervisado" | "semi-autonomo" | "autonomo";

export type ProveedorModelo =
  | "openai"
  | "anthropic"
  | "google"
  | "meta"
  | "mistral"
  | "local"
  | "otro";

export interface RegisterAgentInput {
  name: string;
  autonomyLevel: AutonomyLevel;
  proveedorModelo: ProveedorModelo;
  operatorDid: string;
  publicKeyPem: string;
  metadata?: Record<string, unknown>;
}

export interface RecordActionInput {
  agentId: string;
  action: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  autonomyLevel: AutonomyLevel;
  privateKeyPem: string;
  reasoning?: string;
  humanApproval?: HumanApproval;
}

export interface HumanApproval {
  approverDid: string;
  approvedAt: string;
  signature: string;
}

// ─────────────────────────────────────────────────────────────
// OUTPUTS
// ─────────────────────────────────────────────────────────────

export interface ActionResponse {
  certificate_id: string;
  proof_url: string;
  compliance: {
    eu_ai_act: {
      article_12: string;
      article_14: string;
      article_22: string;
    };
  };
  anchor: {
    tx_hash: string;
    block: number;
    network: string;
    merkle_root: string;
  };
  timestamp_rfc3161: {
    authority: string;
    sealed_at: string;
    token: string;
  };
  signature: {
    classic: string;
    pqc: string;
  };
}

export interface AgentRegistrationResponse {
  agent_id: string;
  agent_did: string;
  contract_id: string;
  contract_url: string;
  created_at: string;
  autonomy_level: string;
  colateral_krn: number;
  limite_dano_krn: number;
}

export interface AgentInfo {
  agent_id: string;
  agent_did: string;
  name: string;
  autonomy_level: string;
  proveedor_modelo: string;
  created_at: string;
  active: boolean;
}

export interface ProofResponse {
  certificate_id: string;
  status: string;
  issued_at: string;
  agent_did: string;
  action: string;
  autonomy_level: string;
  hashes: { sha256: string; sha3: string };
  anchor: { tx_hash: string; network: string; merkle_root: string };
  timestamp: { authority: string; sealed_at: string; token: string };
  verification_url: string;
}

export interface ClientOptions {
  apiKey: string;
  baseUrl?: string;
  timeoutMs?: number;
}