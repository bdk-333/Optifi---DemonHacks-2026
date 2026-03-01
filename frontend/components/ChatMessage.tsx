"use client";

import { User, Bot } from "lucide-react";
import StructuredResponseCard from "./StructuredResponseCard";
import type { StructuredResponse } from "@/lib/api";

export type ChatTurn = {
  id: string;
  role: "user" | "assistant";
  content: string;
  structured?: StructuredResponse;
};

export default function ChatMessage({ turn }: { turn: ChatTurn }) {
  if (turn.role === "user") {
    return (
      <div className="flex gap-3 justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-zinc-700/80 px-4 py-2.5">
          <p className="text-sm text-zinc-100 whitespace-pre-wrap">{turn.content}</p>
        </div>
        <div className="shrink-0 h-8 w-8 rounded-full bg-zinc-600 flex items-center justify-center">
          <User className="h-4 w-4 text-zinc-300" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="shrink-0 h-8 w-8 rounded-full bg-emerald-600/80 flex items-center justify-center">
        <Bot className="h-4 w-4 text-white" />
      </div>
      <div className="min-w-0 max-w-[85%] flex-1">
        {turn.structured ? (
          <StructuredResponseCard data={turn.structured} />
        ) : (
          <div className="rounded-xl border border-zinc-700/60 bg-zinc-800/60 p-4">
            <p className="text-sm text-zinc-300 whitespace-pre-wrap">{turn.content}</p>
          </div>
        )}
      </div>
    </div>
  );
}
