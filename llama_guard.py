"""
Llama Guard is a model fine-tuned to output a safety label, not a rule
validator like Guardrails AI -- hand it an input/output pair, it replies
"safe" or "unsafe" plus MLCommons hazard category codes (S1-S14). Use it as
the last, broadest net behind the specific Guardrails validators.

Runs through any OpenAI-compatible endpoint. Since this project is
otherwise fully local via Ollama, pulling a Llama Guard model there
(`ollama pull llama-guard3`) keeps this step free too -- point
GUARD_BASE_URL at http://localhost:11434/v1 the same way
../ragas-capstone/tests/test_rag_agent.py points at it for its own judge,
with GUARD_API_KEY as any placeholder string. A hosted endpoint (Groq/
Together/Fireworks) works the same way if you'd rather run the full 12B
Llama Guard 4 than what's comfortable on local hardware.

Docs: llama.meta.com (Llama Guard model card, prompt format)
"""

import os

# TODO: from openai import OpenAI
# TODO: client = OpenAI(base_url=os.environ["GUARD_BASE_URL"], api_key=os.environ["GUARD_API_KEY"])
# TODO: LLAMA_GUARD_MODEL = "llama-guard3"  # or your host's model id


# 1. Write llama_guard_check(user_msg, assistant_msg) -> tuple[bool, list[str]]:
#    - Build a messages list: the user turn, then the assistant turn
#      (Llama Guard classifies the LAST turn against the conversation
#      before it -- passing both lets it judge the response in context)
#    - client.chat.completions.create(model=LLAMA_GUARD_MODEL,
#      messages=messages, temperature=0) -- temperature=0 for a
#      deterministic label, this isn't a creative-writing call
#    - Read resp.choices[0].message.content. First line "safe" -> (True, [])
#      Starts with "unsafe" -> (False, [category codes from the next line])
