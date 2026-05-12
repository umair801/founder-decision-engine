"use client";

interface ScoreBarProps {
  label: string;
  score: number;
  maxScore: number;
}

function getScoreColor(percentage: number): string {
  if (percentage >= 75) return "bg-emerald-500";
  if (percentage >= 50) return "bg-blue-500";
  if (percentage >= 25) return "bg-amber-400";
  return "bg-red-400";
}

function getScoreLabel(percentage: number): string {
  if (percentage >= 75) return "Strong";
  if (percentage >= 50) return "Viable";
  if (percentage >= 25) return "Weak";
  return "Critical";
}

function getScoreLabelColor(percentage: number): string {
  if (percentage >= 75) return "text-emerald-600";
  if (percentage >= 50) return "text-blue-600";
  if (percentage >= 25) return "text-amber-600";
  return "text-red-500";
}

export default function ScoreBar({ label, score, maxScore }: ScoreBarProps) {
  const percentage = Math.round((score / maxScore) * 100);
  const colorClass = getScoreColor(percentage);
  const scoreLabel = getScoreLabel(percentage);
  const labelColor = getScoreLabelColor(percentage);

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-sm font-medium text-slate-600 capitalize">
          {label.replace(/_/g, " ")}
        </span>
        <span className="text-sm font-semibold text-slate-700">
          {score}/{maxScore}{" "}
          <span className={`text-xs font-bold ${labelColor}`}>
            ({scoreLabel})
          </span>
        </span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2.5 border border-slate-200">
        <div
          className={`h-2.5 rounded-full transition-all duration-700 ease-out ${colorClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
