# Trailhead Travel Red Team

Adversarial testing and safety layering for Trailhead Travel's
customer-support RAG agent, using [Promptfoo](https://promptfoo.dev)
(automated red-teaming), [Guardrails AI](https://guardrailsai.com)
(output/input validation), and Llama Guard (safety classification). Builds
on the same RAG agent and knowledge base from
[`trailhead-travel-rag-eval`](https://github.com/danteprz9621/trailhead-travel-rag-eval),
unchanged — that project proves the agent answers correctly; this one
proves it holds up under attack.

The core loop: **red-team → guardrail → re-scan**. Promptfoo finds where
the bare RAG agent breaks (prompt injection, RAG-poisoning, jailbreaks,
OWASP LLM Top 10 coverage); Guardrails AI, a reused groundedness gate, and
Llama Guard get layered in front of it; rerunning the identical scan
against the guarded version is what proves whether the break rate actually
dropped, rather than just asserting the guardrails exist.

## Project structure

```
trailhead-travel-red-team/
├── agents/
│   └── rag_agent.py                # unchanged from trailhead-travel-rag-eval
├── data/
│   └── knowledge_base/             # unchanged from trailhead-travel-rag-eval
├── custom-plugins/
│   └── fabricated-policy.yaml      # custom promptfoo plugin (generator + grader) -- not yet wired in, see note below
├── trailhead_travel_provider.py    # promptfoo's call_api() target: input guard -> agent -> output guard -> groundedness gate -> Llama Guard
├── guards.py                       # Guardrails AI input/output Guards (jailbreak detection, toxicity/PII)
├── llama_guard.py                  # Llama Guard safety classifier
├── promptfooconfig.yaml            # purpose, target, 7 built-in/OWASP plugins + a custom policy plugin, 3 strategies
├── requirements.txt
├── .env.example
└── .gitignore
```

**Known gap:** `custom-plugins/fabricated-policy.yaml` (a plugin meant to
specifically probe for fabricated policy figures — a fee or deadline the
knowledge base never covers) has its generator/grader written as design
notes rather than finished prompts, and isn't referenced from
`promptfooconfig.yaml` yet. The scan itself doesn't need it — 7 built-in
plugins (including the full OWASP LLM Top 10 preset) plus a custom
`policy` plugin already run and are what `redteam run` below actually
exercises. This one's a documented stretch goal, not something the rest of
the project depends on.

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

Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` — this is the
one project in the series that isn't free/local end-to-end: `npx promptfoo
redteam run` needs a real key for decent attack generation/grading. The
RAG agent, Guardrails AI, and Llama Guard (via Ollama) all stay free/local
as before; only the promptfoo half costs real, if small, API usage
(`numTests: 3`).

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
