"""
Guardrails AI
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