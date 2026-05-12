"use client";

import { useState } from "react";
import { STAGE_CONFIG, StageName } from "../lib/types";
import { Loader2, Sparkles } from "lucide-react";

interface StageFormProps {
  stage: StageName;
  onSubmit: (values: Record<string, string | number>) => void;
  isLoading: boolean;
  blocked: boolean;
}

export default function StageForm({
  stage,
  onSubmit,
  isLoading,
  blocked,
}: StageFormProps) {
  const config = STAGE_CONFIG.find((s) => s.id === stage);
  const [values, setValues] = useState<Record<string, string | number>>({});

  if (!config) return null;

  function handleChange(key: string, value: string, type: string) {
    setValues((prev) => ({
      ...prev,
      [key]: type === "number" ? Number(value) : value,
    }));
  }

  function handleSubmit() {
    const missing = config!.inputFields
      .filter((f) => f.required && !values[f.key])
      .map((f) => f.label);

    if (missing.length > 0) {
      alert(`Please fill in: ${missing.join(", ")}`);
      return;
    }
    onSubmit(values);
  }

  return (
    <div className="bg-white rounded-2xl p-7 border border-slate-200 shadow-sm">
      {/* Stage header */}
      <div className="flex items-start gap-4 mb-6">
        <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center shrink-0">
          <Sparkles className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-800">{config.label}</h2>
          <p className="text-sm text-slate-500 mt-0.5">{config.description}</p>
        </div>
      </div>

      <div className="space-y-5">
        {config.inputFields.map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">
              {field.label}
              {field.required && (
                <span className="text-red-400 ml-1 font-normal">*</span>
              )}
            </label>

            {field.type === "textarea" ? (
              <textarea
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 resize-none h-28 transition-all"
                placeholder={field.placeholder}
                value={(values[field.key] as string) || ""}
                onChange={(e) =>
                  handleChange(field.key, e.target.value, field.type)
                }
                disabled={isLoading || blocked}
              />
            ) : field.type === "number" ? (
              <input
                type="number"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-all"
                placeholder={field.placeholder}
                value={(values[field.key] as number) || ""}
                onChange={(e) =>
                  handleChange(field.key, e.target.value, field.type)
                }
                disabled={isLoading || blocked}
              />
            ) : (
              <input
                type="text"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-all"
                placeholder={field.placeholder}
                value={(values[field.key] as string) || ""}
                onChange={(e) =>
                  handleChange(field.key, e.target.value, field.type)
                }
                disabled={isLoading || blocked}
              />
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading || blocked}
        className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-sm hover:shadow-indigo-200 hover:shadow-md"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Analyzing...
          </>
        ) : blocked ? (
          "Stage Blocked"
        ) : (
          `Run ${config.label} Analysis`
        )}
      </button>
    </div>
  );
}
