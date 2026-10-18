"""
eval_harness.py — Project 7: Automated Eval Harness

Loops through golden_test_cases.json, sends each question to the bot
(bot.py), checks whether the answer contains the expected keywords, and
prints + saves a report.

Run it:
    python eval_harness.py

Run it again after you change bot.py, its prompt, or policy.md, and compare
the score to the previous run — that's the "catches regressions" part.
"""

import json
import os
from datetime import datetime, timezone

import bot

CASES_PATH = os.path.join(os.path.dirname(__file__), "golden_test_cases.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_cases():
    with open(CASES_PATH, "r") as f:
        return json.load(f)


def score_case(case: dict) -> dict:
    """Run one test case through the bot and grade the answer."""
    actual_answer = bot.answer(case["question"])
    answer_lower = actual_answer.lower()

    missing = [
        phrase for phrase in case["must_include"]
        if phrase.lower() not in answer_lower
    ]
    passed = len(missing) == 0

    return {
        "id": case["id"],
        "question": case["question"],
        "answer": actual_answer,
        "expected_phrases": case["must_include"],
        "missing_phrases": missing,
        "passed": passed,
    }


def run_eval() -> dict:
    cases = load_cases()
    results = [score_case(c) for c in cases]

    total = len(results)
    passed = sum(r["passed"] for r in results)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed,
        "accuracy": round(passed / total, 3) if total else 0,
        "results": results,
    }


def print_report(report: dict) -> None:
    print(f"\n{'='*60}")
    print(f"EVAL RESULTS — {report['passed']}/{report['total']} passed "
          f"({report['accuracy']*100:.0f}% accuracy)")
    print(f"{'='*60}\n")

    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] #{r['id']}: {r['question']}")
        if not r["passed"]:
            print(f"       answer:   {r['answer'][:100]}")
            print(f"       missing:  {r['missing_phrases']}")
    print()


def save_report(report: dict) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = report["timestamp"].replace(":", "-")
    path = os.path.join(RESULTS_DIR, f"eval_{stamp}.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


if __name__ == "__main__":
    report = run_eval()
    print_report(report)
    saved_to = save_report(report)
    print(f"Full report saved to: {saved_to}")
