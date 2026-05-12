"use client";

import { useState } from "react";
import { runFounderStage } from "./lib/api";
import { SessionState, StageName, STAGE_ORDER } from "./lib/types";
import StageProgress from "./components/StageProgress";
import StageForm from "./components/StageForm";
import StageResult from "./components/StageResult";
import { Zap, RotateCcw } from "lucide-react";

const initialSession: SessionState = {
  sessionId: null,
  currentStage: "idea_clarity",
  completedStages: [],
  stageOutputs: {},
  blocked: false,
  blockingMessage: null,
};

export default function Home() {
  const [session, setSession] = useState<SessionState>(initialSession);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<{
    output: Record<string, unknown>;
    supervisorPassed: boolean;
    nextStage: string | null;
    blocked: boolean;
    blockingMessage?: string;
  } | null>(null);

  async function handleStageSubmit(values: Record<string, string | number>) {
    setIsLoading(true);
    setError(null);
    setLastResult(null);

    try {
      const response = await runFounderStage({
        stage: session.currentStage,
        session_id: session.sessionId || undefined,
        ...values,
      });

      setLastResult({
        output: response.output,
        supervisorPassed: response.supervisor_validation.passed,
        nextStage: response.next_stage,
        blocked: response.blocked,
        blockingMessage: response.blocking_message,
      });

      setSession((prev) => ({
        ...prev,
        sessionId: response.session_id,
        blocked: response.blocked,
        blockingMessage: response.blocking_message || null,
        completedStages: response.blocked
          ? prev.completedStages
          : [...prev.completedStages, prev.currentStage],
        stageOutputs: {
          ...prev.stageOutputs,
          [prev.currentStage]: response.output,
        },
      }));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "API call failed. Is the backend running?"
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleContinue() {
    const currentIndex = STAGE_ORDER.indexOf(session.currentStage);
    const nextStage = STAGE_ORDER[currentIndex + 1] as StageName | undefined;
    if (nextStage) {
      setSession((prev) => ({
        ...prev,
        currentStage: nextStage,
        blocked: false,
        blockingMessage: null,
      }));
      setLastResult(null);
    }
  }

  function handleReset() {
    setSession(initialSession);
    setLastResult(null);
    setError(null);
  }

  const showForm = !lastResult || session.blocked;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-slate-800 text-sm">
                Founder Decision Engine
              </span>
              <span className="text-xs text-slate-400 ml-2">by Datawebify</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {session.sessionId && (
              <span className="text-xs text-slate-400 font-mono bg-slate-100 px-2 py-1 rounded-lg">
                {session.sessionId.slice(0, 8)}...
              </span>
            )}
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 border border-slate-200 hover:border-slate-300 px-3 py-1.5 rounded-lg transition-all bg-white hover:bg-slate-50"
            >
              <RotateCcw className="w-3 h-3" />
              New Session
            </button>
          </div>
        </div>
      </header>

      {/* Hero banner — only on first load */}
      {session.currentStage === "idea_clarity" &&
        !lastResult &&
        session.completedStages.length === 0 && (
          <div className="bg-gradient-to-br from-indigo-600 to-violet-600 text-white">
            <div className="max-w-3xl mx-auto px-4 py-10 text-center">
              <div className="inline-flex items-center gap-2 bg-white/10 text-white/90 text-xs font-semibold px-3 py-1.5 rounded-full mb-4 border border-white/20">
                <Zap className="w-3 h-3" />
                AI-Powered Founder OS
              </div>
              <h1 className="text-3xl font-extrabold mb-3 tracking-tight">
                Make structured founder decisions
              </h1>
              <p className="text-indigo-100 text-sm max-w-lg mx-auto leading-relaxed">
                Five AI-enforced stages. Numeric scoring. Zero vague advice.
                Every recommendation is specific, actionable, and validated.
              </p>
              <div className="flex items-center justify-center gap-6 mt-6 text-xs text-indigo-200">
                <span>5 Decision Stages</span>
                <span className="w-1 h-1 rounded-full bg-indigo-300" />
                <span>Numeric Scoring</span>
                <span className="w-1 h-1 rounded-full bg-indigo-300" />
                <span>Hard Gate Logic</span>
                <span className="w-1 h-1 rounded-full bg-indigo-300" />
                <span>AI Supervisor</span>
              </div>
            </div>
          </div>
        )}

      <main className="max-w-3xl mx-auto px-4 py-7 space-y-5">
        {/* Stage Progress */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
          <StageProgress
            currentStage={session.currentStage}
            completedStages={session.completedStages}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 flex gap-2">
            <span className="font-semibold">Error:</span> {error}
          </div>
        )}

        {/* Stage Result */}
        {lastResult && (
          <StageResult
            stage={session.currentStage}
            output={lastResult.output}
            supervisorPassed={lastResult.supervisorPassed}
            blocked={lastResult.blocked}
            blockingMessage={lastResult.blockingMessage}
            nextStage={lastResult.nextStage}
            onContinue={handleContinue}
          />
        )}

        {/* Stage Form */}
        {showForm && (
          <StageForm
            stage={session.currentStage}
            onSubmit={handleStageSubmit}
            isLoading={isLoading}
            blocked={false}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-16 py-6 bg-white">
        <div className="max-w-3xl mx-auto px-4 text-center text-xs text-slate-400">
          Founder Decision Engine — Built by{" "}
          <a
            href="https://datawebify.com"
            className="text-indigo-500 hover:text-indigo-700 font-medium"
          >
            Datawebify
          </a>
        </div>
      </footer>
    </div>
  );
}
