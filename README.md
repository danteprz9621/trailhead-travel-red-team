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
pip install -r requirements.txt

guardrails configure          # one-time, free Hub token
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

## Cost note

Unlike `../deepeval-capstone` and `../ragas-capstone`, this project isn't
free/local end-to-end. `npx promptfoo redteam run` wants a real
`OPENAI_API_KEY` for decent attack generation and grading — the custom
plugin (`custom-plugins/fabricated-policy.yaml`) specifically requires it,
with no local-model fallback. The RAG agent, Guardrails AI, and Llama
Guard (via Ollama) all stay free/local as before; only the promptfoo half
costs real, if small, API usage at `numTests: 3`.
