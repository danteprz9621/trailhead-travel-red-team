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
import asyncio
from agents.rag_agent import ask
from guards import build_input_guard, build_output_guard
from ragas.metrics.collections import Faithfulness
from llama_guard import llama_guard_check
from openai import AsyncOpenAI
from ragas.llms import llm_factory

client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
judge_llm = llm_factory("llama3.1:8b", provider="openai", client=client)
faithfulness = Faithfulness(judge_llm)

REFUSAL = "Sorry, I can't provide an answer to your question."
FAITHFULNESS_MIN = 0.7

def call_api(prompt, options, context):
    try:
        # Input guard for prompt
        try:
            build_input_guard().validate(prompt)
        except Exception:
            return {"output": REFUSAL}

        response = ask(prompt)
        answer = response["answer"]
        retrieved_contexts = response["retrieval_context"]

        # Output guard for answer
        try:
            build_output_guard().validate(answer)
        except Exception:
            return {"output": REFUSAL}

        # Groundedness gate
        faithfulness_score = asyncio.run(
            faithfulness.ascore(
                user_input=prompt,
                response=answer,
                retrieved_contexts=retrieved_contexts,
            )
        ).value
        if faithfulness_score < FAITHFULNESS_MIN:
            return {"output": REFUSAL}

        # 4. Llama Guard -- broadest, most expensive check, last.
        is_safe = llama_guard_check(prompt, answer)
        if not is_safe:
            return {"output": REFUSAL}

        return {"output": answer}
    except Exception as e:
        return {"error": f"provider failed: {e}"}
