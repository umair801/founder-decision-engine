import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface FounderInput {
  stage: string;
  session_id?: string;
  idea_description?: string;
  problem_statement?: string;
  target_customer?: string;
  discovery_notes?: string;
  time_available_hours_per_week?: number;
  capital_available_usd?: number;
  runway_months?: number;
  current_week_number?: number;
  weekly_goals?: string;
}

export interface SupervisorValidation {
  passed: boolean;
  vague_outputs_found: string[];
  missing_fields: string[];
  override_reason?: string;
}

export interface FounderResponse {
  session_id: string;
  stage: string;
  output: Record<string, unknown>;
  supervisor_validation: SupervisorValidation;
  next_stage: string | null;
  blocked: boolean;
  blocking_message?: string;
}

export interface StageInfo {
  stage: string;
  description: string;
}

export async function runFounderStage(
  input: FounderInput
): Promise<FounderResponse> {
  const response = await api.post<FounderResponse>("/api/founder/run", input);
  return response.data;
}

export async function listStages(): Promise<StageInfo[]> {
  const response = await api.get<{ stages: StageInfo[] }>("/api/stages");
  return response.data.stages;
}

export async function healthCheck(): Promise<boolean> {
  try {
    await api.get("/health");
    return true;
  } catch {
    return false;
  }
}