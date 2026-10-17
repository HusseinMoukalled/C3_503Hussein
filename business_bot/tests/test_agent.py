import contextlib
import io
import json
import os
import tempfile
import unittest
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

from agent import (BusinessAgent, build_system_prompt, record_customer_interest,
                   record_feedback, route_message)
from demo_fixture import DemoClient, QueueClient, response, tool_call


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.logs = Path(self.temp.name)
        self.quiet = contextlib.redirect_stdout(io.StringIO())
        self.quiet.__enter__()

    def tearDown(self):
        self.quiet.__exit__(None, None, None)
        self.temp.cleanup()

    def agent(self, client, reflection=False):
        return BusinessAgent(client=client, reflection=reflection, log_dir=self.logs)

    def rows(self, filename):
        return [json.loads(x) for x in (self.logs / filename).read_text(encoding="utf-8").splitlines()]

    def test_knowledge_uses_both_sources(self):
        prompt = build_system_prompt()
        self.assertIn("BUSINESS SUMMARY", prompt)
        self.assertIn("BUSINESS PDF", prompt)
        self.assertIn("Maya Haddad", prompt)
        self.assertIn("PERSONA", prompt)
        self.assertIn("INSTRUCTIONS", prompt)

    def test_three_routes_and_pending_lead(self):
        for text, expected in [("What do you offer?", "general"), ("I want a quote", "lead"),
                               ("Feedback: confusing onboarding", "feedback")]:
            self.assertEqual(route_message(text), expected)
        history = [{"role": "assistant", "content": "May I have your name?"}]
        self.assertEqual(route_message("Sam Demo", history), "lead")
        self.assertEqual(route_message("I'd rather not share", history), "general")

    def test_tools_validate_and_persist(self):
        bad = record_customer_interest("invalid", "Sam", "FAQ bot", log_dir=self.logs)
        self.assertFalse(bad["ok"])
        self.assertFalse((self.logs / "leads.jsonl").exists())
        good = record_customer_interest("sam@example.com", "Sam Demo", "FAQ bot", log_dir=self.logs)
        self.assertTrue(good["ok"])
        self.assertEqual(self.rows("leads.jsonl")[0]["email"], "sam@example.com")
        self.assertTrue(record_feedback("Missing SLA", log_dir=self.logs)["ok"])
        self.assertFalse(record_feedback(" ", log_dir=self.logs)["ok"])

    def test_model_tool_loop_returns_result_to_model(self):
        client = QueueClient([response(calls=[tool_call("record_feedback", {"question": "Unknown SLA?"})],
                                        extra={"extra_content": {"google": {"thought_signature": "test-signature"}}}),
                              response("Your question was saved.")])
        answer = self.agent(client).respond("Unknown SLA?")
        self.assertIn("saved", answer)
        followup = client.requests[1]["messages"]
        self.assertEqual(followup[-1]["role"], "tool")
        self.assertTrue(json.loads(followup[-1]["content"])["ok"])
        self.assertEqual(followup[-2]["extra_content"]["google"]["thought_signature"], "test-signature")
        self.assertIn("tools", client.requests[0])
        self.assertEqual(self.rows("events.jsonl")[-1]["event"], "router_escalation")

    def test_general_response_preserves_history(self):
        client = QueueClient([response("We offer FAQ bots.")])
        history = [{"role": "user", "content": "I run a bakery."},
                   {"role": "assistant", "content": [{"type": "text", "text": "How can I help?"}]}]
        self.agent(client).respond("What do you offer?", history)
        self.assertEqual(client.requests[0]["messages"][1]["content"], "I run a bakery.")
        self.assertEqual(client.requests[0]["messages"][2]["content"], "How can I help?")
        self.assertFalse((self.logs / "leads.jsonl").exists())

    def test_multiturn_lead_and_no_premature_save(self):
        agent = self.agent(DemoClient())
        first = "I'd like a consultation for a bakery FAQ bot."
        answer = agent.respond(first)
        self.assertIn("email", answer)
        self.assertFalse((self.logs / "leads.jsonl").exists())
        agent.respond("My name is Sam Demo and my email is sam@example.com. Please contact me.",
                      [{"role": "user", "content": first}, {"role": "assistant", "content": answer}])
        self.assertEqual(len(self.rows("leads.jsonl")), 1)

    def test_hallucinated_contact_details_rejected(self):
        agent = self.agent(QueueClient([]))
        result = agent.execute_tool("record_customer_interest", {
            "email": "invented@example.com", "name": "Sam Demo", "message": "FAQ bot"}, "I need a FAQ bot")
        self.assertFalse(result["ok"])
        self.assertFalse((self.logs / "leads.jsonl").exists())

    def test_unrecognized_and_invalid_arguments_rejected(self):
        agent = self.agent(QueueClient([]))
        self.assertFalse(agent.execute_tool("delete_everything", {}, "")["ok"])
        self.assertFalse(agent.execute_tool("record_feedback", {"question": 5}, "")["ok"])
        self.assertFalse(agent.execute_tool("record_feedback", {"question": "x", "extra": 5}, "")["ok"])
        call = tool_call("record_feedback", {})
        call.function.arguments = "{bad json"
        client = QueueClient([response(calls=[call]), response("Please retry.")])
        self.agent(client).respond("Feedback: test")
        self.assertFalse(json.loads(client.requests[-1]["messages"][-1]["content"])["ok"])

    def test_duplicate_calls_write_once(self):
        call = lambda: tool_call("record_feedback", {"question": "Repeated feedback"})
        client = QueueClient([response(calls=[call(), call()]), response("Saved.")])
        self.agent(client).respond("Repeated feedback")
        self.assertEqual(len(self.rows("feedback.jsonl")), 1)

    def test_reflection_logs_original_and_revision(self):
        answer = self.agent(DemoClient(), reflection=True).respond("What is your pricing?")
        self.assertNotIn("$500", answer)
        row = self.rows("reflection.jsonl")[0]
        self.assertTrue(row["changed"])
        self.assertIn("$500", row["draft"])

    def test_reflection_failure_keeps_completed_answer(self):
        client = QueueClient([response("Hello."), RuntimeError("Review unavailable")])
        self.assertEqual(self.agent(client, reflection=True).respond("Hello"), "Hello.")
        self.assertEqual(self.rows("events.jsonl")[-1]["event"], "reflection_unavailable")

    def test_disk_error_is_tool_failure(self):
        agent = self.agent(QueueClient([]))
        with patch("agent.log_event", side_effect=OSError("disk full")):
            self.assertFalse(agent.execute_tool("record_feedback", {"question": "Test"}, "Test")["ok"])

    def test_missing_api_key_has_actionable_error(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "Google AI Studio"):
                BusinessAgent().respond("Hello")

    def test_tool_loop_is_bounded(self):
        client = QueueClient([response(calls=[tool_call("record_feedback", {"question": "Feedback"})]) for _ in range(5)])
        self.assertIn("tool-call limit", self.agent(client).respond("Feedback"))
        self.assertEqual(len(self.rows("feedback.jsonl")), 1)

    def test_real_sdk_against_local_http_stub(self):
        """Exercise the installed SDK's HTTP serialization without a provider key."""
        from openai import OpenAI
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append(body)
                if len(requests) == 1:
                    message = {"role": "assistant", "content": None, "tool_calls": [{
                        "id": "http-test-call", "type": "function", "function": {
                            "name": "record_feedback", "arguments": json.dumps({"question": "HTTP integration feedback"})}}]}
                else:
                    message = {"role": "assistant", "content": "Your feedback was saved."}
                payload = json.dumps({"id": "chatcmpl-local-stub", "object": "chat.completion", "created": 0,
                    "model": "test-model", "choices": [{"index": 0, "message": message,
                    "finish_reason": "tool_calls" if len(requests) == 1 else "stop"}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with OpenAI(api_key="local-stub-only", base_url=f"http://127.0.0.1:{server.server_port}/v1/", max_retries=0) as client:
                answer = self.agent(client).respond("Feedback: HTTP integration feedback")
            self.assertIn("saved", answer)
            self.assertEqual(len(requests), 2)
            self.assertEqual(requests[1]["messages"][-1]["tool_call_id"], "http-test-call")
            self.assertTrue(json.loads(requests[1]["messages"][-1]["content"])["ok"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_provider_calls_are_paced(self):
        client = QueueClient([response("Paced reply")])
        agent = self.agent(client)
        agent.live_mode = True
        with patch.dict(os.environ, {"MIN_REQUEST_INTERVAL_SECONDS": "13"}), \
             patch("agent.LAST_REQUEST_AT", 100.0), \
             patch("agent.time.monotonic", side_effect=[105.0, 113.0]), \
             patch("agent.time.sleep") as sleep:
            result = agent.complete(model="test", messages=[])
        sleep.assert_called_once_with(8.0)
        self.assertEqual(result.choices[0].message.content, "Paced reply")


if __name__ == "__main__":
    unittest.main(verbosity=2)
