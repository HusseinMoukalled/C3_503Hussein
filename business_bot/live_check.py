"""Run after adding a real free-tier Gemini key; generates honest live evidence."""
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from agent import BusinessAgent


def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    directory = Path("logs/live_check") / run_id
    agent = BusinessAgent(log_dir=directory)
    history, transcript = [], []
    scenarios = [
        "What services do you offer?",
        "I'd like a consultation for a bakery FAQ bot.",
        "My name is Sam Demo and my email is sam@example.com. Please save my details for follow-up about the bakery FAQ bot.",
        "Feedback: your onboarding instructions were confusing.",
        "Do you offer a guaranteed 24/7 response SLA?",
    ]
    for message in scenarios:
        answer = agent.respond(message, history)
        history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": answer}])
        transcript.append({"user": message, "assistant": answer})
        print("\nUSER:", message, "\nMIRA:", answer)
    assert (directory / "leads.jsonl").exists(), "Live model did not save the lead. Inspect transcript."
    assert len((directory / "feedback.jsonl").read_text().splitlines()) >= 2, "Expected feedback and unanswered-question logs."
    (directory / "transcript.json").write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    print("Live run completed. Review", directory, "and record the Gradio video.")


if __name__ == "__main__":
    main()
