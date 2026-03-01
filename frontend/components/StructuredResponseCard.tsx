"use client";

import { FileText, Lightbulb, ListChecks, Calculator, HelpCircle, AlertCircle } from "lucide-react";
import type { StructuredResponse } from "@/lib/api";

const iconClass = "h-4 w-4 shrink-0 text-emerald-400/90";

export default function StructuredResponseCard({ data }: { data: StructuredResponse }) {
  return (
    <div className="rounded-xl border border-zinc-700/60 bg-zinc-800/60 overflow-hidden shadow-lg">
      {data.summary && (
        <section className="p-4 border-b border-zinc-700/50">
          <div className="flex gap-3">
            <FileText className={iconClass} />
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1">
                Summary
              </h3>
              <p className="text-zinc-200 text-sm leading-relaxed">{data.summary}</p>
            </div>
          </div>
        </section>
      )}
      {data.analysis && (
        <section className="p-4 border-b border-zinc-700/50">
          <div className="flex gap-3">
            <Lightbulb className={iconClass} />
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1">
                Analysis
              </h3>
              <p className="text-zinc-300 text-sm leading-relaxed">{data.analysis}</p>
            </div>
          </div>
        </section>
      )}
      {data.action_plan && data.action_plan.length > 0 && (
        <section className="p-4 border-b border-zinc-700/50">
          <div className="flex gap-3">
            <ListChecks className={iconClass} />
            <div className="min-w-0">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2">
                Action Plan
              </h3>
              <ul className="space-y-1.5">
                {data.action_plan.map((item, i) => (
                  <li
                    key={i}
                    className="flex gap-2 text-sm text-zinc-300"
                  >
                    <span className="text-emerald-400/80 mt-0.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
      {data.calculations && data.calculations.length > 0 && (
        <section className="p-4 border-b border-zinc-700/50">
          <div className="flex gap-3">
            <Calculator className={iconClass} />
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2">
                Calculations
              </h3>
              <dl className="grid gap-1.5 sm:grid-cols-2">
                {data.calculations.map((c, i) => (
                  <div key={i} className="flex justify-between gap-4 py-1 border-b border-zinc-700/40 last:border-0">
                    <dt className="text-zinc-500 text-sm">{c.label}</dt>
                    <dd className="text-zinc-200 text-sm font-medium tabular-nums">{c.value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>
        </section>
      )}
      {data.next_questions && data.next_questions.length > 0 && (
        <section className="p-4 border-b border-zinc-700/50">
          <div className="flex gap-3">
            <HelpCircle className={iconClass} />
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1">
                Next questions
              </h3>
              <ul className="space-y-1 text-sm text-zinc-400">
                {data.next_questions.map((q, i) => (
                  <li key={i}>"{q}"</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
      {data.disclaimer && (
        <section className="p-4 bg-zinc-900/60">
          <div className="flex gap-3">
            <AlertCircle className="h-4 w-4 shrink-0 text-amber-400/80" />
            <p className="text-xs text-zinc-500 italic">{data.disclaimer}</p>
          </div>
        </section>
      )}
    </div>
  );
}
