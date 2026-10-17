"""Run with python app.py, or python app.py --offline-demo for a labelled fixture."""
import argparse
import os

# Keep local startup independent of optional analytics network requests.
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
import gradio as gr

from agent import BusinessAgent


def create_app(offline_demo=False):
    if offline_demo:
        from demo_fixture import DemoClient
        agent = BusinessAgent(client=DemoClient(), log_dir=os.getenv("BOT_LOG_DIR", "logs/offline_demo"))
    else:
        agent = BusinessAgent()

    def chat(message, history):
        try:
            return agent.respond(message, history)
        except ValueError as exc:
            return str(exc)
        except Exception as exc:
            name = type(exc).__name__
            if name == "RateLimitError":
                return "The Gemini API quota is currently exhausted. Wait and retry, or disable reflection to reduce requests."
            if name == "AuthenticationError":
                return "The Gemini API key was rejected. Check your local .env file or Space secret."
            print(f"Chat failed: {name}", flush=True)
            return "The model service is unavailable. Please retry. No unsaved action is being claimed."

    label = ("**OFFLINE VERIFICATION DEMO** - scripted SDK fixture, no live model. "
             "Router and file-writing tools are real. This is not evidence of a live Gemini run."
             if offline_demo else
             "Meet Mira, our virtual concierge. Ask about our services, share feedback, or discuss a project.")
    return gr.ChatInterface(
        fn=chat,
        title="CedarLoop Studio | Mira",
        description=label + "\n\nFictional business for EECE 503P/798S. "
                    "Contact requests save supplied details locally; no email is sent. Use synthetic details for demos.",
        examples=["What services do you offer?", "I'd like a consultation for a bakery FAQ bot.",
                  "My name is Sam Demo and my email is sam@example.com. Please contact me about a bakery FAQ bot.",
                  "Feedback: your onboarding instructions were confusing.",
                  "Do you offer a guaranteed 24/7 response SLA?"],
        cache_examples=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-demo", action="store_true")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "7860")))
    args = parser.parse_args()
    create_app(args.offline_demo).launch(server_name=os.getenv("SERVER_NAME", "127.0.0.1"),
                                        server_port=args.port, share=False)
