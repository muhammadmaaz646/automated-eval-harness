"""
bot.py — the thing being tested.

This is a tiny customer-support bot:
1. load_policy() reads the whole policy.md file (it's short — a few hundred
   words — so there's no need for retrieval/RAG here; that's worth reaching
   for once a knowledge base gets too big to fit in a prompt, not before)
2. answer() sends the full policy doc + the question to Gemini and returns
   whatever Gemini writes back

If no GEMINI_API_KEY is set (in the environment or the local .env file),
answer() falls back to a mock so you can run the whole harness today, right
now, with zero setup — then swap in the real Gemini call once you add your
key.

This file has nothing to do with testing. It's just the bot. The eval
harness (eval_harness.py) is a separate script that calls into this one.
"""

import os

from dotenv import load_dotenv

POLICY_PATH = os.path.join(os.path.dirname(__file__), "policy.md")
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path=ENV_PATH)


def load_policy() -> str:
    with open(POLICY_PATH, "r") as f:
        return f.read()


def _call_gemini(question: str, policy_text: str) -> str:
    """Real call to Gemini. Fill in your key to use this instead of the mock."""
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = (
        "You are a customer support agent. Answer the customer's question "
        "using ONLY the policy text below. Be brief and direct.\n\n"
        f"Policy:\n{policy_text}\n\nQuestion: {question}\nAnswer:"
    )
    # "gemini-flash-latest" is a rolling alias Google keeps pointed at
    # whatever their current Flash model is, so this line survives future
    # model retirements (unlike a pinned version such as "gemini-2.5-flash").
    # Override with the GEMINI_MODEL env var if you ever want to pin one.
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text.strip()


def _mock_answer(question: str, policy_text: str) -> str:
    """
    Offline stand-in for Gemini, so the harness is runnable with no API key.
    It just hands back the whole policy doc — crude, and it'll trivially
    pass every golden test case since the doc contains every required
    phrase somewhere in it. That's expected: the mock only proves the
    harness plumbing works. Real signal on answer quality only shows up
    once you run it against the actual Gemini call below.
    """
    return policy_text


def answer(question: str) -> str:
    policy_text = load_policy()
    if os.environ.get("GEMINI_API_KEY"):
        return _call_gemini(question, policy_text)
    return _mock_answer(question, policy_text)


if __name__ == "__main__":
    # quick manual check
    q = "Can I return a used item?"
    print(f"Q: {q}\nA: {answer(q)}")
