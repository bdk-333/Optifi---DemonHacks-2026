"use client";

import { Target, TrendingUp } from "lucide-react";
import type { Goal } from "@/lib/api";

function GoalProgressBar({ goal }: { goal: Goal }) {
  const current = goal.currentSavings ?? 0;
  const target = goal.targetAmount;
  const pct = target > 0 ? Math.min(100, Math.round((current / target) * 100)) : 0;
  const label = goal.type.replace(/_/g, " ");
  const deadline = goal.deadline ? new Date(goal.deadline).toLocaleDateString("en-US", { month: "short", year: "numeric" }) : "";

  return (
    <div className="rounded-lg bg-zinc-800/80 border border-zinc-700/60 p-3">
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className="text-sm font-medium text-zinc-200 capitalize truncate">
          {label}
        </span>
        <span className="text-xs text-zinc-500 shrink-0">{deadline}</span>
      </div>
      <div className="h-2 rounded-full bg-zinc-700 overflow-hidden">
        <div
          className="h-full rounded-full bg-emerald-500/90 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-zinc-500">
        <span>${current.toLocaleString()} / ${target.toLocaleString()}</span>
        <span>{pct}%</span>
      </div>
    </div>
  );
}

export default function Sidebar({
  goals,
  loading,
  onRefresh,
}: {
  goals: Goal[];
  loading: boolean;
  onRefresh: () => void;
}) {
  return (
    <aside className="w-72 shrink-0 flex flex-col border-r border-zinc-800 bg-zinc-900/50">
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2 text-zinc-100">
          <TrendingUp className="h-6 w-6 text-emerald-400" />
          <h2 className="font-semibold text-lg">OptiFi</h2>
        </div>
      </div>
      <div className="p-4 flex-1 overflow-auto">
        <div className="flex items-center justify-between mb-3">
          <span className="flex items-center gap-2 text-sm font-medium text-zinc-300">
            <Target className="h-4 w-4 text-emerald-400" />
            Goal Progress
          </span>
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="text-xs text-emerald-400 hover:text-emerald-300 disabled:opacity-50"
          >
            {loading ? "…" : "Refresh"}
          </button>
        </div>
        {loading && goals.length === 0 ? (
          <div className="text-sm text-zinc-500 animate-pulse">Loading goals…</div>
        ) : goals.length === 0 ? (
          <p className="text-sm text-zinc-500">No goals yet. Add one from chat.</p>
        ) : (
          <div className="space-y-3">
            {goals.map((g) => (
              <GoalProgressBar key={g.id} goal={g} />
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

