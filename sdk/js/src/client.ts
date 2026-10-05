/**
 * Atribución SDK — Cliente HTTP.
 *
 * Uso:
 *   import { AtribucionClient } from "@atribucion/sdk";
 *
 *   const client = new AtribucionClient({ apiKey: "ak_live_..." });
 *
 *   const agent = await client.registerAgent({
 *     name: "MiAgente",
 *     autonomyLevel: "semi-autonomo",
 *     proveedorModelo: "anthropic",
 *     operatorDid: "did:kronos:human:0x...",
 *     publicKeyPem: pubPem,
 *   });
 *
 *   const cert = await client.recordAction({
 *     agentId: agent.agent_id,
 *     action: "trade_executed",
 *     input: { symbol: "AAPL" },
 *     output: { status: "filled" },
 *     reasoning: "Señal alcista.",
 *     autonomyLevel: "semi-autonomo",
 *     privateKeyPem: privHex,
 *   });
 */

import {
  signHybridPqcPlaceholder,
  signPayload,
} from "./crypto.js";

import type {
  ActionResponse,
  AgentInfo,
  AgentRegistrationResponse,
  ClientOptions,
  ProofResponse,
  RecordActionInput,
  RegisterAgentInput,
} from "./types.js";

const DEFAULT_BASE_URL = "https://api.atribucion.io";
const DEFAULT_TIMEOUT = 30_000;

export class AtribucionClient {
  private apiKey: string;
  private baseUrl: string;
  private timeoutMs: number;

  constructor(options: ClientOptions) {
    if (!options.apiKey) {
      throw new Error("apiKey es obligatorio");
    }
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT;
  }

  // ─── AGENTES ─────────────────────────────────────────────────

  async registerAgent(
    input: RegisterAgentInput
  ): Promise<AgentRegistrationResponse> {
    const response = await this.request("POST", "/v1/agents", {
      name: input.name,
      autonomy_level: input.autonomyLevel,
      proveedor_modelo: input.proveedorModelo,
      operator_did: input.operatorDid,
      public_key_pem: input.publicKeyPem,
      metadata: input.metadata ?? {},
    });

    return response as AgentRegistrationResponse;
  }

  async getAgent(agentId: string): Promise<AgentInfo> {
    return (await this.request("GET", `/v1/agents/${agentId}`)) as AgentInfo;
  }

  // ─── ACCIONES ────────────────────────────────────────────────

  async recordAction(input: RecordActionInput): Promise<ActionResponse> {
    const payload = {
      action: input.action,
      input: input.input,
      output: input.output,
      reasoning: input.reasoning ?? null,
      autonomy_level: input.autonomyLevel,
      human_approval: input.humanApproval ?? null,
    };

    const sigClassic = signPayload(input.privateKeyPem, payload);
    const sigPqc = signHybridPqcPlaceholder(payload);

    return (await this.request(
      "POST",
      `/v1/agents/${input.agentId}/actions`,
      payload,
      {
        "X-Agent-Signature": sigClassic,
        "X-Agent-Signature-PQC": sigPqc,
      }
    )) as ActionResponse;
  }

  // ─── VERIFICACIÓN ────────────────────────────────────────────

  async verifyCertificate(certificateId: string): Promise<ProofResponse> {
    const response = await fetch(
      `${this.baseUrl}/v1/proofs/${certificateId}`,
      {
        method: "GET",
        signal: AbortSignal.timeout(this.timeoutMs),
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail ?? `Error HTTP ${response.status}`);
    }

    return (await response.json()) as ProofResponse;
  }

  // ─── REPORTES ────────────────────────────────────────────────

  async getMonthlyReport(period: string): Promise<Record<string, unknown>> {
    return (await this.request(
      "GET",
      `/v1/reports/${period}`
    )) as Record<string, unknown>;
  }

  async downloadMonthlyReportPdf(period: string): Promise<Uint8Array> {
    const response = await fetch(
      `${this.baseUrl}/v1/reports/${period}.pdf`,
      {
        method: "GET",
        headers: { Authorization: `Bearer ${this.apiKey}` },
        signal: AbortSignal.timeout(this.timeoutMs),
      }
    );

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    return new Uint8Array(await response.arrayBuffer());
  }

  // ─── INTERNO ─────────────────────────────────────────────────

  private async request(
    method: string,
    path: string,
    body?: unknown,
    extraHeaders?: Record<string, string>
  ): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
        "User-Agent": "atribucion-sdk-js/0.1.0",
        ...extraHeaders,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(this.timeoutMs),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(
        error.detail ?? `Error HTTP ${response.status} en ${method} ${path}`
      );
    }

    return response.json();
  }
}

RUTA 

sdk/js/src/index.ts

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
