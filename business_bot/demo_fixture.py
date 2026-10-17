"""Scripted SDK-shaped responses for OFFLINE verification, never a substitute LLM.

No network calls occur here. Normal app.py does not use this module.
"""
import json
import re
from types import SimpleNamespace
from uuid import uuid4


class Message:
    def __init__(self, content=None, calls=None, extra=None):
        self.content = content
        self.tool_calls = calls or []
        self.extra = extra or {}

    def model_dump(self, exclude_none=True):
        result = {"role": "assistant", **self.extra}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [{"id": c.id, "type": "function", "function": {
                "name": c.function.name, "arguments": c.function.arguments}} for c in self.tool_calls]
        return result


def tool_call(name, arguments):
    return SimpleNamespace(id="call_" + uuid4().hex[:12], type="function",
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)))


def response(content=None, calls=None, extra=None):
    return SimpleNamespace(choices=[SimpleNamespace(message=Message(content, calls, extra))])


class QueueClient:
    """Inject explicit responses and inspect exact outgoing requests in tests."""
    def __init__(self, responses):
        self.responses, self.requests = list(responses), []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        import copy
        self.requests.append(copy.deepcopy(kwargs))
        if not self.responses:
            raise AssertionError("Unexpected extra model request")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class DemoClient:
    """Limited canned scenarios for an explicitly labelled local verification video."""
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        messages = kwargs["messages"]
        if "tools" not in kwargs:  # Canned reflection reviewer.
            payload = json.loads(messages[-1]["content"])
            draft = payload["draft"]
            if "$500" in draft:
                draft = "Project pricing is custom quoted after discovery. We offer a free 20-minute introductory consultation."
            return response(draft)
        last = messages[-1]
        if last["role"] == "tool":
            outcome = json.loads(last["content"])
            if not outcome["ok"]:
                return response("I couldn't save this record: " + outcome["error"])
            calls = next(m["tool_calls"] for m in reversed(messages) if m.get("tool_calls"))
            name = calls[-1]["function"]["name"]
            if name == "record_customer_interest":
                return response("Thanks, Sam. I've saved your name, email, and bakery FAQ bot notes for follow-up. This saves a lead; it does not send an email or book a meeting.")
            original = next(m["content"] for m in reversed(messages) if m["role"] == "user")
            if "SLA" in original or "guaranteed" in original:
                return response("Our business documents don't specify a guaranteed 24/7 response SLA. I've logged your question for the team rather than guessing.")
            return response("Thanks for sharing that. I've saved your feedback about the onboarding instructions for the team.")
        text = last["content"]
        all_user = "\n".join(m["content"] for m in messages if m["role"] == "user")
        if "feedback" in text.lower():
            return response(calls=[tool_call("record_feedback", {"question": text})])
        if "SLA" in text or "guaranteed" in text or "drones" in text:
            return response(calls=[tool_call("record_feedback", {"question": text})])
        if "sam@example.com" in all_user and "Sam Demo" in all_user and (
            "sam@example.com" in text or "contact me" in text.lower()
        ):
            return response(calls=[tool_call("record_customer_interest", {
                "email": "sam@example.com", "name": "Sam Demo", "message": "Bakery FAQ bot consultation requested."})])
        if "consultation" in text.lower() or "interested" in text.lower():
            return response("I'd be happy to discuss a bakery FAQ bot. May I have your name and your email address? I'll save them with your project notes for follow-up.")
        if "price" in text.lower() or "pricing" in text.lower():
            # Intentionally flawed fixture draft so the optional reviewer visibly corrects it.
            return response("Our project price is $500.")
        if re.search(r"rather not|no thanks|don't save", text, re.I):
            return response("Of course. You can continue asking about our services without sharing contact details.")
        return response("CedarLoop offers workflow discovery, a knowledge-grounded FAQ chatbot, lead capture, feedback logging, and staff handover training. We work with small businesses in English and Arabic.")
