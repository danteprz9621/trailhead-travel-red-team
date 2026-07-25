"""
Guardrails AI mental model: Validator (one check on a string) -> Guard (a
composable pipeline of validators) -> on_fail (what happens when a
validator fails: EXCEPTION/FIX/REASK/REFRAIN/NOOP). For a safety gate,
on_fail=EXCEPTION is usually right -- it hard-blocks rather than silently
repairing a violation, which matters: FIX on a PII leak can ship a
redacted-but-still-leaky answer.

Setup (run once, outside this file):
    pip install guardrails-ai
    guardrails configure
    guardrails hub install hub://guardrails/detect_pii
    guardrails hub install hub://guardrails/toxic_language
    guardrails hub install hub://guardrails/detect_jailbreak

Docs: guardrails.dev (Guard, Validators, on_fail actions)
"""

from guardrails import Guard, OnFailAction
from guardrails.hub import ToxicLanguage, DetectPII, DetectJailbreak

# Output guard: Trailhead Travel must never emit toxic language or leak PII.
def build_output_guard():
    return Guard().use(
        ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail=OnFailAction.EXCEPTION),
        DetectPII(pii_entities=["EMAIL_ADDRESS"], on_fail=OnFailAction.EXCEPTION)
    )

# Input guard: screens the raw prompt before any model call is spent on it.
def build_input_guard():
    return Guard().use(
        DetectJailbreak(on_fail=OnFailAction.EXCEPTION))

if __name__ == "__main__":
    guard = build_output_guard()
    guard.validate("Your flight departs at 10am from gate B12.")  # should pass
    try:
        guard.validate("You idiot, email me at dante@example.com.")
        print("NO GUARDRAIL FIRED -- bug")
    except Exception as e:
        print("Blocked:", e)