"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

export default function ChatInput({
  onSend,
  disabled,
  placeholder = "Ask about goals, budgets, or loans…",
}: {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  const [value, setValue] = useState("");
  const valueRef = useRef(value);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  valueRef.current = value;

  const send = (e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmed = (valueRef.current ?? value).trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const canSend = Boolean(value.trim()) && !disabled;

  return (
    <form
      onSubmit={send}
      className="flex gap-2 items-end p-4 border-t border-zinc-800 bg-zinc-900/30"
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        disabled={disabled}
        className="flex-1 min-h-[44px] max-h-40 resize-none rounded-lg border border-zinc-700 bg-zinc-800/80 px-4 py-3 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 disabled:opacity-50 text-sm"
      />
      <button
        type="submit"
        disabled={!canSend}
        title="Send message"
        aria-label="Send message"
        className="shrink-0 h-11 w-11 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center text-white transition-colors"
      >
        <Send className="h-5 w-5" />
      </button>
    </form>
  );
}
