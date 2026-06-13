# Resource 1: Setup Checklist

**Feature 1 · AI Engineering Bootcamp · BlockseBlock**

Use this checklist the first time you run the project. Each step is a checkbox — tick it off as you go.

---

## Pre-flight Checklist

### Python & Environment

- [ ] Python 3.11 or newer is installed
  - Check: open a terminal and run `python3 --version` (or `python --version` on Windows)
  - Expected: `Python 3.11.x` or higher
  - If missing: follow [SETUP.md — Step 1](../../../SETUP.md#step-1--install-python-311)

- [ ] You are inside the project's root folder in your terminal
  - Check: run `ls` (Mac/Linux) or `dir` (Windows) — you should see `README.md`, `shared/`, etc.

- [ ] Virtual environment is created
  - Command: `python3 -m venv venv`
  - Only needed once per machine

- [ ] Virtual environment is **active** — you see `(venv)` at the start of your terminal prompt
  - Mac/Linux: `source venv/bin/activate`
  - Windows CMD: `venv\Scripts\activate`
  - Windows PowerShell: `venv\Scripts\Activate.ps1`

- [ ] Packages are installed
  - Command (from repo root): `pip install -r requirements.txt`
  - You should see many lines of "Downloading …" and end with "Successfully installed"

---

### Configuration

- [ ] `.env` file exists in the repo root
  - Create it: `cp .env.example .env` (Mac/Linux) or `copy .env.example .env` (Windows)

- [ ] `LLM_PROVIDER` is set in `.env` (e.g. `LLM_PROVIDER=openai`)
  - See [docs/provider-setup-guide.md](../../provider-setup-guide.md) to pick your provider

- [ ] Your provider's API key is set in `.env`
  - e.g. `OPENAI_API_KEY=sk-...` if using OpenAI
  - The value should be your real key — not `your-api-key-here`

- [ ] Model name is set (e.g. `OPENAI_MODEL=gpt-4o-mini`)

---

### Running Feature 1

- [ ] You are in the `starter/` (or `solution/`) folder for this feature
  - Command: `cd week-1-brain/feature-1-hello-ai/starter`

- [ ] Server starts without errors
  - Command: `uvicorn main:app --reload --port 8000`
  - Expected last line: `INFO: Application startup complete.`

- [ ] Swagger UI is accessible at `http://localhost:8000/docs`

- [ ] Chat UI is accessible at `http://localhost:8000`

- [ ] `/api/health` returns `{"status": "ok"}` when clicked in Swagger

---

## Troubleshooting Table

| Error | What it means | Fix |
|-------|--------------|-----|
| `AuthenticationError` or `401` | API key is wrong or missing | Open `.env`, check `OPENAI_API_KEY` (or your provider's key) is set correctly |
| `RuntimeError: LLM_PROVIDER=... but OPENAI_API_KEY is not set` | Provider mismatch | Make sure the key for your chosen provider is set in `.env` |
| `Can't reach Ollama at http://localhost:11434` | Ollama isn't running | Run `ollama serve` in a separate terminal window |
| `ModuleNotFoundError: No module named 'fastapi'` | Packages not installed, or venv not active | Activate venv (`source venv/bin/activate`), then `pip install -r requirements.txt` |
| `422 Unprocessable Entity` on `/api/chat` | Request is missing the `message` field | Make sure you've completed Step 1 (added `message: str` to `ChatRequest`) |
| `Address already in use` | Port 8000 is taken by another process | Add `--port 8001` to the uvicorn command; visit `http://localhost:8001/docs` |
| Server starts but `/api/chat` returns `500` | `chat()` function returns `None` | You haven't implemented Step 2 yet — the `pass` statement returns nothing |
| `FileNotFoundError` for `.env` | `.env` doesn't exist | Run `cp .env.example .env` from the repo root |

---

## You're Ready

When all boxes are checked and `/api/chat` returns a real reply from the model, you've completed Feature 1.

Head back to [Feature 1 README](../README.md) for the stretch challenges and a preview of Feature 2.
