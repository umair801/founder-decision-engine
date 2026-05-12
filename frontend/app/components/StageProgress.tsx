"use client";

import { CheckCircle, Circle, Lock } from "lucide-react";
import { StageName, STAGE_CONFIG } from "../lib/types";

interface StageProgressProps {
  currentStage: StageName;
  completedStages: StageName[];
}

export default function StageProgress({
  currentStage,
  completedStages,
}: StageProgressProps) {
  return (
    <div className="w-full py-5 px-4">
      <div className="flex items-start justify-between relative">
        {/* Connector line */}
        <div className="absolute top-5 left-8 right-8 h-0.5 bg-slate-200 z-0" />

        {STAGE_CONFIG.map((stage, index) => {
          const isCompleted = completedStages.includes(stage.id);
          const isActive = currentStage === stage.id;
          const isLocked =
            !isCompleted &&
            !isActive &&
            index > STAGE_CONFIG.findIndex((s) => s.id === currentStage);

          return (
            <div
              key={stage.id}
              className="flex flex-col items-center z-10 flex-1"
            >
              {/* Icon */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 shadow-sm transition-all duration-300
                  ${
                    isCompleted
                      ? "bg-emerald-500 border-emerald-500 shadow-emerald-100"
                      : isActive
                      ? "bg-indigo-600 border-indigo-600 shadow-indigo-100 shadow-md"
                      : "bg-white border-slate-200"
                  }`}
              >
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5 text-white" />
                ) : isLocked ? (
                  <Lock className="w-4 h-4 text-slate-300" />
                ) : (
                  <Circle className="w-5 h-5 text-indigo-500" />
                )}
              </div>

              {/* Label */}
              <span
                className={`mt-2 text-xs text-center font-semibold max-w-[72px] leading-tight
                  ${
                    isCompleted
                      ? "text-emerald-600"
                      : isActive
                      ? "text-indigo-600"
                      : "text-slate-400"
                  }`}
              >
                {stage.label}
              </span>

              {/* Active dot */}
              {isActive && (
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
