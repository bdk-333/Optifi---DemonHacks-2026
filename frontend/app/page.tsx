"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import ChatMessage, { type ChatTurn } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import { getGoals, postChat, type Goal, type StructuredResponse } from "@/lib/api";

const DEMO_USER_ID = "demo-user-id";

function useGoals(userId: string) {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getGoals(userId);
      setGoals(res.goals ?? []);
    } catch {
      setGoals([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { goals, loading, refresh };
}

export default function ChatPage() {
  const userId = DEMO_USER_ID;
  const { goals, loading, refresh } = useGoals(userId);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sending, setSending] = useState(false);

  const handleSend = useCallback(
    async (message: string) => {
      const userTurn: ChatTurn = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
      };
      setTurns((prev) => [...prev, userTurn]);
      setSending(true);
      try {
        const data: StructuredResponse = await postChat(userId, message);
        const assistantTurn: ChatTurn = {
          id: `asst-${Date.now()}`,
          role: "assistant",
          content: data.summary,
          structured: data,
        };
        setTurns((prev) => [...prev, assistantTurn]);
      } catch {
        const errorTurn: ChatTurn = {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Could not reach the assistant. Check the API is running and try again.",
        };
        setTurns((prev) => [...prev, errorTurn]);
      } finally {
        setSending(false);
      }
    },
    [userId]
  );

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <Sidebar goals={goals} loading={loading} onRefresh={refresh} />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="shrink-0 border-b border-zinc-800 px-6 py-4">
          <h1 className="text-lg font-semibold text-zinc-100">Chat</h1>
          <p className="text-sm text-zinc-500 mt-0.5">
            Ask about goals, budgets, or loans. Responses appear as structured cards below.
          </p>
        </header>
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-6">
            {turns.length === 0 && (
              <div className="rounded-xl border border-dashed border-zinc-700/60 bg-zinc-900/30 p-8 text-center">
                <p className="text-zinc-500 text-sm">
                  Send a message to start. Try: “How much do I need to save monthly for a $12,000 goal by next year?”
                </p>
              </div>
            )}
            {turns.map((turn) => (
              <ChatMessage key={turn.id} turn={turn} />
            ))}
          </div>
        </div>
        <ChatInput onSend={handleSend} disabled={sending} />
      </div>
    </div>
  );
}
