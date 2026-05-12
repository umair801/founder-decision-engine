// Stage names as a union type — only these 5 values are valid
export type StageName =
  | "idea_clarity"
  | "customer_discovery"
  | "validation"
  | "financial_reality"
  | "weekly_execution";

// Stage display metadata
export interface StageConfig {
  id: StageName;
  label: string;
  description: string;
  inputFields: InputField[];
}

export interface InputField {
  key: string;
  label: string;
  placeholder: string;
  type: "text" | "textarea" | "number";
  required: boolean;
}

// Idea Clarity output shape
export interface IdeaClarityOutput {
  scores: {
    problem_clarity: number;
    target_customer_specificity: number;
    differentiation: number;
    founder_market_fit: number;
  };
  total_score: number;
  verdict: "strong" | "viable" | "weak" | "invalid";
  gap_analysis: string[];
  required_next_action: string;
}

// Customer Discovery output shape
export interface CustomerDiscoveryOutput {
  discovery_readiness_score: number;
  interview_questions: string[];
  readiness_verdict: "ready" | "not_ready";
  blocking_gaps: string[];
  required_actions: string[];
}

// Validation output shape
export interface ValidationOutput {
  scores: {
    problem_confirmation: number;
    willingness_to_pay: number;
    competitive_landscape: number;
    tam_estimate: number;
  };
  total_score: number;
  verdict: "validated" | "partially_validated" | "not_validated";
  confidence_score: number;
  recommended_next_step: string;
}

// Financial Reality output shape
export interface FinancialRealityOutput {
  estimated_build_cost_usd: number;
  estimated_time_to_first_revenue_months: number;
  break_even_estimate_months: number;
  financial_viability_score: number;
  recommendation: "go" | "no_go" | "pivot";
  reasoning: string;
}

// Weekly Execution output shape
export interface WeeklyAction {
  task: string;
  priority: number;
  time_estimate_hours: number;
  success_criterion: string;
}

export interface WeeklyExecutionOutput {
  week_number: number;
  actions: WeeklyAction[];
}

// Session state tracked in the frontend
export interface SessionState {
  sessionId: string | null;
  currentStage: StageName;
  completedStages: StageName[];
  stageOutputs: Partial<Record<StageName, Record<string, unknown>>>;
  blocked: boolean;
  blockingMessage: string | null;
}

// Stage order for progression logic
export const STAGE_ORDER: StageName[] = [
  "idea_clarity",
  "customer_discovery",
  "validation",
  "financial_reality",
  "weekly_execution",
];

// Stage display config — labels and input fields per stage
export const STAGE_CONFIG: StageConfig[] = [
  {
    id: "idea_clarity",
    label: "Idea Clarity",
    description: "Score your idea across 4 dimensions",
    inputFields: [
      {
        key: "idea_description",
        label: "Idea Description",
        placeholder: "Describe your idea in 2-3 sentences",
        type: "textarea",
        required: true,
      },
      {
        key: "problem_statement",
        label: "Problem Statement",
        placeholder: "What specific problem does this solve?",
        type: "textarea",
        required: true,
      },
    ],
  },
  {
    id: "customer_discovery",
    label: "Customer Discovery",
    description: "Validate your target customer hypothesis",
    inputFields: [
      {
        key: "target_customer",
        label: "Target Customer",
        placeholder: "Who exactly is your customer? Be specific.",
        type: "textarea",
        required: true,
      },
    ],
  },
  {
    id: "validation",
    label: "Validation",
    description: "Score your market validation evidence",
    inputFields: [
      {
        key: "discovery_notes",
        label: "Discovery Notes",
        placeholder: "Paste your interview notes or findings here",
        type: "textarea",
        required: true,
      },
    ],
  },
  {
    id: "financial_reality",
    label: "Financial Reality",
    description: "Calculate your financial viability",
    inputFields: [
      {
        key: "time_available_hours_per_week",
        label: "Hours Per Week Available",
        placeholder: "20",
        type: "number",
        required: true,
      },
      {
        key: "capital_available_usd",
        label: "Capital Available (USD)",
        placeholder: "5000",
        type: "number",
        required: true,
      },
      {
        key: "runway_months",
        label: "Runway (Months)",
        placeholder: "6",
        type: "number",
        required: true,
      },
    ],
  },
  {
    id: "weekly_execution",
    label: "Weekly Execution",
    description: "Get your structured action plan",
    inputFields: [
      {
        key: "current_week_number",
        label: "Current Week Number",
        placeholder: "1",
        type: "number",
        required: true,
      },
      {
        key: "weekly_goals",
        label: "Weekly Goals",
        placeholder: "What do you want to achieve this week?",
        type: "textarea",
        required: true,
      },
    ],
  },
];