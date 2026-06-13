# AI Engineering Bootcamp

**BlockseBlock · Instructor: Naureen Fathima**

> Build a production-ready, domain-specific AI assistant — one feature per week, twelve weeks from zero to shipped.

---

## What You'll Build

By the end of this bootcamp, you will have a running web application that:

- Chats intelligently about **your chosen domain** (healthcare, HR, education, e-commerce, and more)
- Answers questions from **your own documents** — not just what the model was trained on
- Executes **real actions** on your behalf: looks things up, calls APIs, schedules tasks
- Accepts **voice input** and speaks answers back
- Runs in **Docker** and is ready to share with the world

This is not a series of isolated demos. Every feature you build in Week 1 is still running — and improved — in Week 12.

---

## The 4-Phase Story

| Phase | Week | Theme | What happens |
|-------|------|-------|--------------|
| 🧠 **Brain** | 1 | Talk to an LLM | You give the model a voice, a name, and a mission |
| 📚 **Knowledge** | 2 | Feed it your data | The model learns from documents you provide |
| 🤝 **Hands** | 3 | Give it abilities | The model can take actions, not just answer |
| 🚀 **Launch** | 4 | Ship it | Package, harden, and deploy your finished product |

---

## The 12-Feature Map

| # | Phase | Feature Title | What You Build | Cumulative Capability After This Feature |
|---|-------|---------------|----------------|------------------------------------------|
| 1 | 🧠 Brain | Basic Chat | `POST /chat` endpoint | User sends a message, gets a reply |
| 2 | 🧠 Brain | System Prompt | Domain persona config | Assistant has a name, role, and domain focus |
| 3 | 🧠 Brain | Conversation Memory | Session-based history | Assistant remembers what was said earlier |
| 4 | 📚 Knowledge | Document Upload | `POST /documents/upload` | User uploads a PDF or `.txt` file |
| 5 | 📚 Knowledge | Chunking & Embeddings | Background indexing pipeline | Uploaded docs are split into searchable pieces |
| 6 | 📚 Knowledge | RAG | Retrieval-augmented `/chat` | Assistant answers from your documents |
| 7 | 🤝 Hands | Structured Outputs | JSON response schemas | Assistant returns parseable data, not just prose |
| 8 | 🤝 Hands | Tool Calling | Function registry | Assistant calls Python functions you define |
| 9 | 🤝 Hands | Agent Loop | Autonomous task runner | Assistant plans and executes multi-step tasks |
| 10 | 🚀 Launch | Voice (STT + TTS) | `/voice` endpoints | Speak to and hear from your assistant |
| 11 | 🚀 Launch | Docker & Health Checks | `Dockerfile` + `/health` | App runs in a container, ready to deploy |
| 12 | 🚀 Launch | Production Polish | Rate limiting, logging | Enterprise-grade reliability and observability |

---

## Repo Layout

```
ai-engineering-bootcamp/
├── README.md              ← you are here
├── SETUP.md               ← start here if you're setting up for the first time
├── GLOSSARY.md            ← plain-English definitions for every term used in the videos
├── .env.example           ← copy this to .env and fill in your API key
├── requirements.txt       ← Python packages for the whole course
│
├── shared/                ← code every feature reuses (LLM client, config, models)
├── ui/                    ← the single-page web interface (grows each week)
│
├── week-1-brain/          ← Features 1–3
├── week-2-knowledge/      ← Features 4–6
├── week-3-hands/          ← Features 7–9
├── week-4-launch/         ← Features 10–12
│
└── docs/                  ← guides, architecture diagrams, student project gallery
```

Each week folder contains one subfolder per feature, and each feature has two sub-folders:

```
feature-N-title/
├── solution/   ← complete, runnable code you can reference at any time
└── starter/    ← same files, but this week's new logic is stubbed with TODO comments
```

**Following along with a video?** Open `starter/` and fill in the TODOs.  
**Stuck?** Peek at `solution/`.  
**Starting mid-course?** Every feature's `solution/` is fully runnable standalone — you can jump in at any week.

---

## Getting Started

1. **Read [SETUP.md](SETUP.md)** — covers Python installation all the way through running the server.
2. **Pick your domain** — see the callout below and [docs/domain-picker.md](docs/domain-picker.md).
3. Open `week-1-brain/feature-1-basic-chat/starter/` and watch Video 1.

---

> ### Pick Your Domain
>
> This bootcamp uses **Alpine Trail Co.** — a fictional outdoor gear retailer — as its running example.  
> But the real goal is for you to build *your* assistant for *your* domain.
>
> Before you start Week 1, spend 10 minutes choosing your domain.  
> It will make every exercise more meaningful and your final project more impressive.
>
> **→ [Choose your domain](docs/domain-picker.md)** — eight ready-to-go examples with starter documents and agent actions included.

---

## Reference

| Document | Purpose |
|----------|---------|
| [SETUP.md](SETUP.md) | Install Python, create a virtual environment, run the server |
| [GLOSSARY.md](GLOSSARY.md) | Plain-English definitions for LLM, RAG, token, agent, and 20+ more terms |
| [docs/domain-picker.md](docs/domain-picker.md) | Choose and customize your project domain |
| [docs/student-projects.md](docs/student-projects.md) | See what other students built |
| [docs/architecture/](docs/architecture/) | System diagrams added week by week |
