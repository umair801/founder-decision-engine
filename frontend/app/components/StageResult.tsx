"use client";

import { CheckCircle, XCircle, AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";
import ScoreBar from "./ScoreBar";
import { StageName } from "../lib/types";

interface StageResultProps {
  stage: StageName;
  output: Record<string, unknown>;
  supervisorPassed: boolean;
  blocked: boolean;
  blockingMessage?: string;
  nextStage: string | null;
  onContinue: () => void;
}

function VerdictBadge({ verdict }: { verdict: string }) {
  const colors: Record<string, string> = {
    strong: "bg-emerald-50 text-emerald-700 border-emerald-200",
    viable: "bg-blue-50 text-blue-700 border-blue-200",
    validated: "bg-emerald-50 text-emerald-700 border-emerald-200",
    partially_validated: "bg-amber-50 text-amber-700 border-amber-200",
    go: "bg-emerald-50 text-emerald-700 border-emerald-200",
    weak: "bg-orange-50 text-orange-700 border-orange-200",
    not_validated: "bg-red-50 text-red-700 border-red-200",
    not_ready: "bg-red-50 text-red-700 border-red-200",
    ready: "bg-emerald-50 text-emerald-700 border-emerald-200",
    no_go: "bg-red-50 text-red-700 border-red-200",
    pivot: "bg-amber-50 text-amber-700 border-amber-200",
    invalid: "bg-red-50 text-red-700 border-red-200",
  };

  const colorClass =
    colors[verdict] || "bg-slate-50 text-slate-600 border-slate-200";

  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border ${colorClass}`}
    >
      {verdict.replace(/_/g, " ")}
    </span>
  );
}

export default function StageResult({
  stage,
  output,
  supervisorPassed,
  blocked,
  blockingMessage,
  nextStage,
  onContinue,
}: StageResultProps) {
  const scores = output.scores as Record<string, number> | undefined;
  const totalScore =
    (output.total_score as number) ||
    (output.financial_viability_score as number) ||
    (output.discovery_readiness_score as number) ||
    null;

  const verdict =
    (output.verdict as string) ||
    (output.readiness_verdict as string) ||
    (output.recommendation as string) ||
    null;

  const nextAction =
    (output.required_next_action as string) ||
    (output.recommended_next_step as string) ||
    null;

  const gapAnalysis = output.gap_analysis as string[] | undefined;
  const requiredActions = output.required_actions as string[] | undefined;
  const interviewQuestions = output.interview_questions as string[] | undefined;
  const actions = output.actions as Record<string, unknown>[] | undefined;
  const reasoning = output.reasoning as string | undefined;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header bar */}
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck
            className={`w-4 h-4 ${supervisorPassed ? "text-emerald-500" : "text-amber-500"}`}
          />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            AI Supervisor: {supervisorPassed ? "Output Validated" : "Flagged"}
          </span>
        </div>
        {verdict && <VerdictBadge verdict={verdict} />}
      </div>

      <div className="px-6 py-6 space-y-6">
        {/* Total Score */}
        {totalScore !== null && (
          <div className="flex items-center justify-between bg-slate-50 rounded-xl px-5 py-4 border border-slate-100">
            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                Overall Score
              </div>
              <div className="text-4xl font-extrabold text-slate-800">
                {totalScore}
                <span className="text-lg font-normal text-slate-400 ml-1">
                  / 100
                </span>
              </div>
            </div>
            <div
              className={`w-16 h-16 rounded-full flex items-center justify-center text-lg font-bold border-4
              ${
                totalScore >= 75
                  ? "border-emerald-400 text-emerald-600 bg-emerald-50"
                  : totalScore >= 50
                  ? "border-blue-400 text-blue-600 bg-blue-50"
                  : totalScore >= 25
                  ? "border-amber-400 text-amber-600 bg-amber-50"
                  : "border-red-400 text-red-600 bg-red-50"
              }`}
            >
              {totalScore}
            </div>
          </div>
        )}

        {/* Score Breakdown */}
        {scores && Object.keys(scores).length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
              Score Breakdown
            </h3>
            {Object.entries(scores).map(([key, value]) => (
              <ScoreBar
                key={key}
                label={key.replace(/_/g, " ")}
                score={value}
                maxScore={25}
              />
            ))}
          </div>
        )}

        {/* Interview Questions */}
        {interviewQuestions && interviewQuestions.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
              Discovery Interview Questions
            </h3>
            <ol className="space-y-3">
              {interviewQuestions.map((q, i) => (
                <li
                  key={i}
                  className="flex gap-3 bg-indigo-50 rounded-xl px-4 py-3 border border-indigo-100"
                >
                  <span className="text-indigo-600 font-bold shrink-0 text-sm">
                    {i + 1}.
                  </span>
                  <span className="text-sm text-slate-700">{q}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Gap Analysis */}
        {gapAnalysis && gapAnalysis.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
              Gap Analysis
            </h3>
            <ul className="space-y-2">
              {gapAnalysis.map((gap, i) => (
                <li
                  key={i}
                  className="flex gap-3 bg-orange-50 rounded-xl px-4 py-3 border border-orange-100"
                >
                  <XCircle className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                  <span className="text-sm text-slate-700">{gap}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weekly Actions */}
        {actions && actions.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
              This Week&apos;s Action Plan
            </h3>
            <div className="space-y-3">
              {actions.map((action, i) => (
                <div
                  key={i}
                  className="bg-slate-50 rounded-xl p-4 border border-slate-200"
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <span className="text-sm font-semibold text-slate-800">
                      {action.task as string}
                    </span>
                    <span className="text-xs bg-indigo-600 text-white px-2.5 py-1 rounded-lg shrink-0 font-bold">
                      P{action.priority as number}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500">
                    {action.time_estimate_hours as number}h to complete —{" "}
                    <span className="text-slate-600">
                      {action.success_criterion as string}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Financial Reasoning */}
        {reasoning && (
          <div className="bg-slate-50 rounded-xl px-4 py-4 border border-slate-200">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
              Reasoning
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed">{reasoning}</p>
          </div>
        )}

        {/* Next Action */}
        {nextAction && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl px-4 py-4">
            <h3 className="text-xs font-bold text-indigo-500 uppercase tracking-widest mb-2">
              Required Next Action
            </h3>
            <p className="text-sm text-indigo-800 font-medium">{nextAction}</p>
          </div>
        )}

        {/* Blocking Message */}
        {blocked && blockingMessage && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-4">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <h3 className="text-xs font-bold text-red-500 uppercase tracking-widest">
                Stage Blocked
              </h3>
            </div>
            <p className="text-sm text-red-700">{blockingMessage}</p>
          </div>
        )}

        {/* Required Actions */}
        {requiredActions && requiredActions.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
              Required Actions to Unlock Next Stage
            </h3>
            <ul className="space-y-2">
              {requiredActions.map((action, i) => (
                <li
                  key={i}
                  className="flex gap-3 bg-amber-50 rounded-xl px-4 py-3 border border-amber-100"
                >
                  <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <span className="text-sm text-slate-700">{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Continue Button */}
        {!blocked && nextStage && (
          <button
            onClick={onContinue}
            className="w-full bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-sm hover:shadow-emerald-200 hover:shadow-md"
          >
            Continue to{" "}
            {nextStage
              .split("_")
              .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
              .join(" ")}
            <ArrowRight className="w-4 h-4" />
          </button>
        )}

        {/* All complete */}
        {!blocked && !nextStage && (
          <div className="text-center py-4 bg-emerald-50 rounded-xl border border-emerald-100">
            <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="text-emerald-700 font-bold">All 5 stages complete</p>
            <p className="text-sm text-emerald-600 mt-1">
              Your founder decision engine run is finished.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
