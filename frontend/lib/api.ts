const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type Goal = {
  id: string;
  type: string;
  targetAmount: number;
  deadline: string;
  priority: number;
  currentSavings?: number;
};

export type GoalsResponse = {
  goals: Goal[];
};

export type CalculationItem = {
  label: string;
  value: string;
};

export type StructuredResponse = {
  summary: string;
  analysis: string;
  action_plan: string[];
  calculations: CalculationItem[];
  next_questions: string[];
  disclaimer: string;
};

export async function getGoals(userId: string): Promise<GoalsResponse> {
  const res = await fetch(`${API_BASE}/goals?userId=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error("Failed to fetch goals");
  return res.json();
}

export async function postChat(
  userId: string,
  message: string
): Promise<StructuredResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId, message }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}
