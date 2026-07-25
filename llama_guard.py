"""
Llama Guard
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url=os.environ["GUARD_BASE_URL"], api_key=os.environ["GUARD_API_KEY"])

# Llama Guard classifies the LAST turn against the conversation before it,
# so both the user prompt and the assistant's answer get passed in.
def llama_guard_check(user_msg, assitant_msg) -> tuple[bool, list[str]]:
    resp = client.chat.completions.create(
        temperature=0,
        model = "llama-guard3",
        messages= [
            {"role":"user", "content":user_msg},
            {"role":"assistant", "content":assitant_msg}
        ]
    )

    lines = resp.choices[0].message.content.strip().splitlines()
    is_safe = lines[0].strip().lower() == "safe"
    return is_safe
