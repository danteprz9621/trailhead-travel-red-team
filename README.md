# Promptfoo Red-Teaming + Guardrails Practice Project

A practice project for adversarial testing and safety layering on top of a
RAG agent, using [Promptfoo](https://promptfoo.dev) (red-teaming),
[Guardrails AI](https://guardrailsai.com) (output/input validation), and
Llama Guard (safety classification). Reuses the "Trailhead Travel" RAG
agent and knowledge base from [`../ragas-capstone`](../ragas-capstone),
unchanged.

The loop this project builds toward: **red-team → guardrail → re-scan**.
Promptfoo finds where the bare RAG agent breaks; Guardrails AI, a reused
groundedness gate, and Llama Guard get layered in front of it; rerunning
the identical scan against the guarded version is what proves whether the
break rate actually dropped.

## Project structure

```
promptfoo-redteam-practice/
├── agents/
│   └── rag_agent.py                # unchanged from ragas-capstone
├── data/
│   └── knowledge_base/             # unchanged from ragas-capstone
├── custom-plugins/
│   └── fabricated-policy.yaml      # SKELETON: custom promptfoo plugin (generator + grader)
├── trailhead_travel_provider.py    # SKELETON: promptfoo's call_api(), all 4 defense layers
├── guards.py                       # SKELETON: Guardrails AI input/output Guards
├── llama_guard.py                  # SKELETON: Llama Guard safety classifier
├── promptfooconfig.yaml            # SKELETON: purpose, target, plugins, strategies
├── requirements.txt
├── .env.example
└── .gitignore
```

Every file marked SKELETON has numbered comments describing what to
build, no implementation — same pattern as `../ragas-capstone`'s test
files.

## Setup

```bash
node --version   # need 18+; promptfoo runs via npx, nothing to install upfront
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install --only-binary=:all: -r requirements.txt
```

`--only-binary=:all:` matters on Windows with a recent Python (3.13+):
plain `pip install` tries to build `litellm` (a `guardrails-ai` dependency)
from source, which needs a Rust/Cargo toolchain and fails without one.
Forcing wheels-only skips that and installs a working version instead.

```bash
guardrails configure          # one-time, free Hub token

# PowerShell -- needed before the hub installs below, or they crash with
# UnicodeEncodeError trying to print a checkmark on success (Windows
# console default codepage can't encode it):
$env:PYTHONIOENCODING="utf-8"

guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_jailbreak
```

Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` — see
[Cost note](#cost-note) below for why this project, unlike the other two,
isn't free/local end-to-end.

For Llama Guard, either pull a local model:

```bash
ollama pull llama-guard3
```

or point `GUARD_BASE_URL`/`GUARD_API_KEY` in `.env` at a hosted
OpenAI-compatible endpoint (Groq/Together/Fireworks) instead.

## Running it

```bash
npx promptfoo@latest redteam run      # generate attacks + eval against the target
npx promptfoo@latest redteam report   # open the severity-ranked HTML report
```

Build `trailhead_travel_provider.py` and `promptfooconfig.yaml` first —
`redteam run` needs both to do anything. Get a baseline scan against the
bare (unguarded) provider before building `guards.py`/`llama_guard.py` and
wiring them in, then rerun the identical scan to compare break rates
before/after.
