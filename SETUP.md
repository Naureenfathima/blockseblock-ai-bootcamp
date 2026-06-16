# Setup Guide

**AI Engineering Bootcamp · BlockseBlock**

This guide assumes you have never used a terminal before. Every step is explained from scratch. Follow along top-to-bottom and you'll have the server running in under 20 minutes.

---

## What We're Setting Up

| Piece | What it does |
|-------|--------------|
| Python 3.11+ | The programming language the whole course runs on |
| Virtual environment (`venv`) | An isolated box so your packages don't interfere with other projects |
| `requirements.txt` packages | The libraries your code needs (FastAPI, OpenAI SDK, etc.) |
| `.env` file | Where you put your API key — kept private, never committed to git |
| `uvicorn` | The web server that runs your FastAPI app |

---

## Step 1 — Install Python 3.11+

### Windows

1. Open your browser and go to [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Click the yellow **"Download Python 3.11.x"** button (or any 3.11/3.12/3.13 version).
3. Run the downloaded `.exe` file.
4. **Important:** On the first screen, tick the checkbox **"Add Python to PATH"** before clicking Install.
5. Click **Install Now**.
6. When it finishes, click **Close**.

To verify it worked, open **Command Prompt** (press `Win + R`, type `cmd`, press Enter) and run:

```
python --version
```

You should see something like `Python 3.11.9`. If you see `Python 2.x`, try `python3 --version` instead.

### macOS

macOS ships with an old Python — we need a newer one.

1. Install **Homebrew** (a package manager for Mac) if you don't have it. Open **Terminal** (press `Cmd + Space`, type `terminal`, press Enter) and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen prompts. This takes a few minutes.

2. Then install Python:

```bash
brew install python@3.11
```

3. Verify:

```bash
python3 --version
```

### Linux (Ubuntu/Debian)

Open **Terminal** and run:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
```

Verify:

```bash
python3.11 --version
```

---

## Step 2 — Open a Terminal in the Project Folder

You need to navigate your terminal to this project's folder. The folder is wherever you saved or cloned this repo.

**Windows:** Open **File Explorer**, navigate to the project folder, then in the address bar at the top type `cmd` and press Enter. A terminal opens in that folder.

**macOS:** Open **Terminal**, then drag the project folder from Finder into the Terminal window — it will type the path for you. Then type `cd ` (with a space) before the path, and press Enter. Or: right-click the folder in Finder → **New Terminal at Folder** (if available).

**Linux:** Right-click the project folder → **Open Terminal Here**.

To confirm you're in the right place, run:

```bash
ls
```

You should see files like `README.md`, `requirements.txt`, and folders like `shared/`.

---

## Step 3 — Create a Virtual Environment

A virtual environment is a private folder where Python packages are installed just for this project. Think of it like a dedicated toolbox for this job.

Run:

```bash
python3 -m venv venv
```

(On Windows, use `python` instead of `python3` if `python3` is not recognised.)

This creates a folder called `venv/` inside your project. You only do this once.

---

## Step 4 — Activate the Virtual Environment

Every time you open a new terminal to work on this project, you must activate the environment before anything else.

**Windows (Command Prompt):**

```
venv\Scripts\activate
```

**Windows (PowerShell):**

```
venv\Scripts\Activate.ps1
```

If PowerShell says "running scripts is disabled", run this first:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again.

**macOS / Linux:**

```bash
source venv/bin/activate
```

When activation works, your terminal prompt will change — you'll see `(venv)` at the start of the line. That means everything from this point goes into your private toolbox.

---

## Step 5 — Install the Required Packages

With the virtual environment active, run:

```bash
pip install -r requirements.txt
```

This reads `requirements.txt` and installs all the libraries the course needs. It may take 1–3 minutes on the first run.

---

## Step 6 — Choose Your AI Provider

Before configuring your `.env` file, decide which AI provider you'll use. This course supports four options:

| Provider | What you need | Best for |
|----------|---------------|---------|
| **OpenAI** | API key from platform.openai.com | Smoothest experience, all 12 features including voice |
| **Anthropic** | API key from console.anthropic.com | High-quality responses; add `VOICE_PROVIDER=openai` for Feature 10 |
| **Cohere** | API key from dashboard.cohere.com (free trial) | Good for chat and RAG; add `VOICE_PROVIDER=openai` for Feature 10 |
| **Ollama** | Install from ollama.com — no key needed | Completely free and private; runs on your own machine |

For detailed instructions, see **[docs/provider-setup-guide.md](docs/provider-setup-guide.md)**.

**Short answer for most students:** if you're not sure, use **OpenAI** — it's the most reliable across all 12 features.

---

## Step 7 — Set Up Your Environment Variables

Environment variables are like secret configuration values — they live outside your code so you never accidentally share your API key.

1. Copy the example file:

**macOS / Linux:**

```bash
cp .env.example .env
```

**Windows:**

```
copy .env.example .env
```

2. Open the new `.env` file in any text editor (Notepad, VS Code, TextEdit, etc.).

3. Fill in your values. Set `LLM_PROVIDER` to your chosen provider, then fill in that provider's section. For example, if you chose OpenAI:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

Replace `your-actual-api-key-here` with the API key from your provider. If you chose Ollama, you only need:

```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

(No key needed for Ollama — but `ollama serve` must be running.)

**Never share this file or commit it to git.** The `.gitignore` in this repo already prevents it from being uploaded.

---

## Step 8 — Run the Server

Navigate into the feature folder you're working on. For example, Feature 1:

```bash
cd week-1-brain/feature-1-hello-ai/solution
```

Then start the server:

```bash




```

What each part means:
- `uvicorn` — the web server program
- `main:app` — look in `main.py`, find the variable called `app`
- `--reload` — restart automatically when you save a file (great for development)
- `--port 8000` — listen on port 8000

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

To stop the server, press `Ctrl + C`.

---

## Step 9 — Explore the API (Swagger UI)

FastAPI automatically generates interactive documentation. Open your browser and go to:

```
http://localhost:8000/docs
```

You'll see a list of all your API endpoints. You can click any of them, fill in test data, and click **Execute** to try them out — no separate tool needed.

---

## Step 10 — Open the Web UI

The `ui/` folder contains a browser-based interface that grows each week. You have two options:

**Option A — Open directly (simplest):**  
Double-click `ui/index.html` in your file manager, or drag it into a browser window.

**Option B — Serve it from FastAPI (recommended from Feature 2 onward):**  
With the server running, go to `http://localhost:8000/` in your browser.

---

## Common Errors and Fixes

### `AuthenticationError` or `401 Unauthorized`

**What it means:** Your API key is missing or wrong.

**Fix:**
1. Open your `.env` file and check that `LLM_API_KEY` is set to your actual key (not `your-api-key-here`).
2. Make sure you saved the file after editing.
3. Restart the uvicorn server — it reads the `.env` on startup.

---

### `Can't reach Ollama at http://localhost:11434`

**What it means:** You've set `LLM_PROVIDER=ollama` but the Ollama server isn't running.

**Fix:**
1. Make sure Ollama is installed ([ollama.com](https://ollama.com)).
2. Open a **new, separate terminal window** and run:

```bash
ollama serve
```

Keep that terminal window open. Now restart your uvicorn server in the original terminal.

---

### `422 Unprocessable Entity`

**What it means:** You sent a request to an endpoint, but the data you sent was missing a required field or had the wrong format.

**Fix:**
1. Open Swagger at `http://localhost:8000/docs`.
2. Click the failing endpoint and look at the **Request body** schema — it shows exactly what fields are expected.
3. Make sure your request includes all required fields with the correct types (e.g., strings in quotes, numbers without quotes).

---

### `ModuleNotFoundError: No module named 'fastapi'` (or any other module)

**What it means:** The package isn't installed, or you forgot to activate the virtual environment.

**Fix:**
1. Check that `(venv)` appears in your terminal prompt. If not, activate it (see Step 4).
2. Run `pip install -r requirements.txt` again.

---

### `[Errno 48] Address already in use` (macOS/Linux) or `Only one usage of each socket address` (Windows)

**What it means:** Something else is already running on port 8000.

**Fix — Option A:** Stop whatever is using port 8000.

Find and kill it (macOS/Linux):

```bash
lsof -i :8000
kill -9 <PID>
```

(Replace `<PID>` with the number from the `PID` column in the `lsof` output.)

**Fix — Option B:** Use a different port:

```bash
uvicorn main:app --reload --port 8001
```

Then visit `http://localhost:8001/docs`.

---

### `python: command not found` (macOS/Linux)

**What it means:** Your system uses `python3` instead of `python`.

**Fix:** Replace `python` with `python3` in every command. For example:

```bash
python3 -m venv venv
```

---

## You're Ready

Once you can see the Swagger UI at `http://localhost:8000/docs`, you're set up. Head back to [README.md](README.md) and start Week 1.
