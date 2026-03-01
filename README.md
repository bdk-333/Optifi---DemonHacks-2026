# OptiFi

Full-stack AI financial assistant (FastAPI + Next.js). Follow these steps to run the project on a new machine.

## Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend; Next.js 14 requires 18.17+ — upgrade from Node 16 to avoid install warnings)
- **Git** (to clone and share the repo)

## Backend (FastAPI)

1. **Create and activate a virtual environment** (recommended so dependencies stay isolated and reproducible):

   **Windows (PowerShell):**

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **Windows (CMD):**

   ```cmd
   cd backend
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   **macOS / Linux:**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):

   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env   # macOS/Linux
   # Edit .env; for local LLM see "Using Ollama" below.
   ```

4. **Using Ollama (local LLM, no API key):**

   The chat assistant uses **Ollama** by default for intent classification (no OpenAI key needed).

   - Install [Ollama](https://ollama.com) and run: `ollama run llama3.2` (or another model).
   - Ensure Ollama is running (default: `http://localhost:11434`).
   - Optional: set `OLLAMA_BASE_URL` or `OLLAMA_MODEL` in `.env` if you use a different URL or model.
   - To use OpenAI instead, set `OPENAI_API_KEY` in `.env`.

5. **Run the API:**

   ```bash
   uvicorn app.main:app --reload
   ```

   API runs at `http://localhost:8000`.

## Frontend (Next.js)

1. **Install dependencies** (from project root or frontend folder):

   ```bash
   cd frontend
   npm install
   ```

   This creates `node_modules` and updates `package-lock.json` so anyone else gets the same versions.

2. **Configure environment** (optional):

   ```bash
   copy .env.example .env.local   # Windows
   # cp .env.example .env.local   # macOS/Linux
   # Set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 if the API is elsewhere
   ```

3. **Run the dev server:**

   ```bash
   npm run dev
   ```

   App runs at `http://localhost:3000`.

## Sharing the code

- Commit **backend/requirements.txt** and **frontend/package.json** + **frontend/package-lock.json**.
- Do **not** commit **backend/.venv**, **frontend/node_modules**, or **.env** (they are in `.gitignore`).
- On a new machine: clone the repo, then run the backend and frontend setup steps above. No need to commit virtual env or node_modules.

## Quick start (both apps)

From project root:

```bash
# Terminal 1 – backend
cd backend && python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt && uvicorn app.main:app --reload

# Terminal 2 – frontend
cd frontend && npm install && npm run dev
```

Then open `http://localhost:3000` for the UI and `http://localhost:8000/docs` for the API docs.

## Stopping the services

- **If you have the terminals open:** press **Ctrl+C** in the terminal running the backend and in the one running the frontend.
- **If you don’t:** stop the process using the port, then start again when needed.

  **Windows (PowerShell)** — stop backend (port 8000) and one frontend (e.g. 3004):

  ```powershell
  # Backend (port 8000)
  $b = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($b) { Stop-Process -Id $b -Force }

  # Frontend (change 3004 to the port Next.js is using if different)
  $f = Get-NetTCPConnection -LocalPort 3004 -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($f) { Stop-Process -Id $f -Force }
  ```

  **Windows (CMD)** — find PIDs with `netstat -ano | findstr ":8000"` and `netstat -ano | findstr ":3004"`, then `taskkill /PID <pid> /F` for each.
# Optifi---DemonHacks-2026
