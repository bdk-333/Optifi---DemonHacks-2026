# OptiFi — Codebase Map

Use this order to read the code and understand how everything fits together. Follow it when debugging or adding features.

---

## 1. Entry points (where things start)

| File                          | Purpose                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------- |
| **`backend/app/main.py`**     | FastAPI app: CORS, mounted routers. All API traffic starts here.                                      |
| **`frontend/app/layout.tsx`** | Root layout and global CSS. Wraps every page.                                                         |
| **`frontend/app/page.tsx`**   | Chat page: state (messages, goals), `handleSend` → calls API, renders Sidebar + messages + ChatInput. |

Read these first so you know where the backend and frontend begin.

---

## 2. API routes (what the frontend calls)

| File                              | Endpoints                                                                                                                           | When to look                                                                 |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **`backend/app/routes/chat.py`**  | `POST /chat` — body: `userId`, `message`. Parses goal from message, builds context, runs orchestrator, returns structured response. | Fix chat behavior, add request/response fields, change how context is built. |
| **`backend/app/routes/goals.py`** | `GET /goals?userId=...` — returns list of goals for sidebar.                                                                        | Change what goals are returned, add filters, or wire to a real DB.           |

Routes are the only place that receive HTTP requests; everything else is called from here.

---

## 3. Chat flow (how a message becomes a reply)

Follow this sequence when tracing a single chat message:

1. **`backend/app/routes/chat.py`**
   - Receives `POST /chat`.
   - `route_intent(body.message)` → get intent (goal / budget / loan / general).
   - `_build_context(userId, message)` → parse goal (amount, deadline, etc.) and/or load stored goals.
   - `run_intent(intent, context, body.message)` → run the right agent.
   - Returns `StructuredResponse`.

2. **`backend/app/agents/orchestrator.py`**
   - **`route_intent(message)`** — keyword match first, then LLM fallback (`llm_service.classify_intent`).
   - **`run_intent(intent, context, message)`** — dispatches to goal / budget / loan agent or general placeholder.
   - **`_run_goal(context, message)`** — if context has `target_amount` and `deadline`, calls `goal_service.plan_goal` then `goal_agent.format_goal_response`; otherwise returns “add target and deadline” message.

3. **`backend/app/services/goal_service.py`**
   - **`plan_goal(...)`** — pure math: months remaining, monthly required, feasible or not, recommendations. No LLM.

4. **`backend/app/agents/goal_agent.py`**
   - **`format_goal_response(plan)`** — turns `GoalPlanResult` into the standard response shape: summary, analysis, action_plan, calculations, next_questions, disclaimer.

5. **`backend/app/services/llm_service.py`**
   - **`classify_intent(message)`** — used only when keywords don’t match. Calls Ollama or OpenAI to return one intent label.

So: **route → orchestrator → (goal_service + goal_agent)** or placeholder. LLM is only for intent when the message is ambiguous.

---

## 4. Goal parsing and storage

| File                                   | Purpose                                                                                                                                                                      |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **`backend/app/utils/goal_parser.py`** | **`parse_goal_from_message(message)`** — regex extraction of amount, deadline, optional current_savings, monthly_surplus. Used in `chat.py` to build context and save goals. | Change how “$12k by next year” is parsed; add new date/amount formats. |
| **`backend/app/store.py`**             | In-memory goal store: **`get_goals(user_id)`**, **`add_goal(...)`**. Used by `chat.py` and `goals.py`.                                                                       | Replace with DB, add update/delete, or change goal shape.              |

Understanding these two explains why some messages create goals and others don’t, and why the sidebar shows what it shows.

---

## 5. Data shapes (request/response and DB)

| File                              | Purpose                                                                                                                                                                            |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **`backend/app/schemas/chat.py`** | **`ChatRequest`** (userId, message), **`StructuredResponse`** (summary, analysis, action_plan, calculations, next_questions, disclaimer), **`CalculationItem`**.                   | Add or rename response fields; frontend must match. |
| **`backend/app/schemas/goal.py`** | **`GoalOut`**, **`GoalsResponse`** — what `GET /goals` returns.                                                                                                                    | Change goal fields for API or sidebar.              |
| **`backend/app/models/*.py`**     | SQLModel tables (e.g. **`user.py`**, **`goal.py`**, **`budget.py`**, **`transaction.py`**). Not used by current in-memory store but define DB schema for when you add persistence. | Add tables or columns; run migrations.              |

Use schemas when you change API contracts; use models when you add or change stored data.

---

## 6. Frontend (how the UI talks to the backend)

| File                                                 | Purpose                                                                                                                                                                                                   |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **`frontend/lib/api.ts`**                            | **`getGoals(userId)`**, **`postChat(userId, message)`**, types (`Goal`, `StructuredResponse`, etc.). Base URL from env.                                                                                   | Change API URL, add endpoints, or response types.            |
| **`frontend/app/page.tsx`**                          | Chat page: **`useGoals(userId)`** (loads/refreshes goals), **`handleSend`** (appends user message, calls `postChat`, appends assistant turn with `structured`). Renders Sidebar, message list, ChatInput. | Add loading/error UI, change how messages or goals are used. |
| **`frontend/components/Sidebar.tsx`**                | Goal Progress: list of goals, progress bar per goal (currentSavings / targetAmount), refresh button.                                                                                                      | Change sidebar layout or what’s shown per goal.              |
| **`frontend/components/ChatInput.tsx`**              | Text input + submit (form submit and Enter). Calls **`onSend(message)`**.                                                                                                                                 | Change input behavior or validation.                         |
| **`frontend/components/ChatMessage.tsx`**            | Renders one message: user bubble or assistant card.                                                                                                                                                       | Change message layout.                                       |
| **`frontend/components/StructuredResponseCard.tsx`** | Renders assistant **StructuredResponse**: Summary, Analysis, Action Plan, Calculations, Next questions, Disclaimer.                                                                                       | Change how the backend response is displayed.                |

Flow: **page** → **api** (getGoals, postChat) → **Sidebar** (goals) and **ChatMessage** (turns); **StructuredResponseCard** displays the backend’s structured reply.

---

## 7. Quick reference by task

| You want to…                                      | Look at…                                                                                                                                 |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Change what the chat API accepts or returns       | `backend/app/schemas/chat.py`, `backend/app/routes/chat.py`, `frontend/lib/api.ts`, `StructuredResponseCard.tsx`                         |
| Fix or improve goal parsing (“$12k by next year”) | `backend/app/utils/goal_parser.py`, `backend/app/routes/chat.py` (\_build_context)                                                       |
| Change how intent is chosen (keywords or LLM)     | `backend/app/agents/orchestrator.py`, `backend/app/services/llm_service.py`                                                              |
| Change goal math (monthly required, feasibility)  | `backend/app/services/goal_service.py`, `backend/app/agents/goal_agent.py`                                                               |
| Change what goals the sidebar shows               | `backend/app/routes/goals.py`, `backend/app/store.py`, `frontend/components/Sidebar.tsx`                                                 |
| Add a new intent (e.g. tax, budget)               | `backend/app/agents/orchestrator.py` (keywords + run_intent branch), add agent and/or service, optionally `llm_service.py` INTENT_LABELS |
| Add a new API endpoint                            | `backend/app/main.py` (include_router), new file under `backend/app/routes/`, then `frontend/lib/api.ts` and the component that calls it |
| Change UI styling or layout                       | `frontend/app/globals.css`, `frontend/tailwind.config.ts`, and the component you’re changing                                             |

---

## 8. Suggested reading order (first time)

1. **`backend/app/main.py`** — see app and routes.
2. **`backend/app/routes/chat.py`** — see how a message becomes a response.
3. **`backend/app/agents/orchestrator.py`** — see routing and goal flow.
4. **`backend/app/services/goal_service.py`** + **`backend/app/agents/goal_agent.py`** — see goal math and response shape.
5. **`backend/app/utils/goal_parser.py`** + **`backend/app/store.py`** — see where goals come from and where they’re stored.
6. **`frontend/app/page.tsx`** — see how the UI sends a message and displays replies.
7. **`frontend/lib/api.ts`** — see exact API calls and types.
8. **`frontend/components/StructuredResponseCard.tsx`** — see how the backend response is rendered.

After that, use the “Quick reference by task” table to jump to the right file when checking for errors or adding a feature.
