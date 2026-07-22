"""
promptfoo calls this file's call_api(prompt, options, context) once per
adversarial test case -- it's the "target" promptfoo attacks (see
promptfooconfig.yaml's targets: section).

This is also where the Part 2 defense layers (Guardrails AI, a
groundedness gate, Llama Guard) get wired in, in front of the same
agents/rag_agent.py that ../ragas-capstone already tests for quality -- the
guardrail must live in the same code path promptfoo hits, or re-scanning
after adding one proves nothing.

Docs: promptfoo.dev/docs/red-team/configuration/ (Custom Providers section)
"""

from agents.rag_agent import ask

# TODO (step 2): from guards import build_output_guard, build_input_guard
# TODO (step 5): from llama_guard import llama_guard_check


# 1. Write the plain, unguarded version first, and a REFUSAL constant it'll
#    share with every later step:
#    REFUSAL = "..."  (a safe, generic decline message)
#    def call_api(prompt, options, context):
#        try:
#            answer = ask(prompt)["answer"]
#            return {"output": answer}
#        except Exception as e:
#            return {"error": f"provider failed: {e}"}
#    Get this working end-to-end against promptfooconfig.yaml before adding
#    any guard -- it's the baseline every later scan gets compared against.


# 2. Add the output guard (build_output_guard() from guards.py, built once
#    at import time): validate the answer before returning it. If the
#    guard raises, catch it and return REFUSAL instead of the raw answer --
#    a refusal is a *safe* response promptfoo should see as a pass, so
#    don't let this exception fall through to the outer except in step 1.


# 3. Add the input guard (build_input_guard() from guards.py): validate
#    `prompt` BEFORE calling ask() at all, and return REFUSAL without
#    spending a model call if it fails. Remember from the course: this
#    can't catch indirect prompt injection smuggled inside retrieved
#    knowledge-base content, since that text only exists *after*
#    retrieval -- the input guard only ever sees the raw incoming prompt.


# 4. Add the groundedness gate: reuse a Faithfulness check the same way
#    ../ragas-capstone/tests/test_rag_agent.py does (AsyncOpenAI +
#    llm_factory pointed at Ollama, ragas.metrics.collections.Faithfulness,
#    scored via asyncio.run(faithfulness.ascore(...))) -- but here it's a
#    threshold gate, not a score to assert on: below your chosen minimum,
#    return REFUSAL instead of the answer. ask() already returns
#    retrieval_context, so you have everything ascore() needs.


# 5. Add Llama Guard as the last, broadest check: llama_guard_check(prompt,
#    answer) from llama_guard.py. If it comes back unsafe, return REFUSAL
#    -- and consider logging the returned category codes (e.g. "S6")
#    somewhere you can see them later, they're useful for a before/after
#    writeup.


# 6. Assemble the full call_api(prompt, options, context) with all four
#    layers in order -- input guard, then ask(), then output guard, then
#    the groundedness gate, then Llama Guard, then return the answer --
#    cheapest/most specific check first, broadest/most expensive last.
#    Keep the outer try/except from step 1 around the whole thing for
#    genuine crashes (as opposed to a guard/gate refusing on purpose).
