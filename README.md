# CedarLoop Studio Business Assistant

EECE 503P/798S — C3: Introduction to Agents  
Hussein Moukalled

Mira is a virtual assistant for CedarLoop Studio, a fictional business automation
company. It answers questions using a business profile PDF and text summary, collects
customer leads, and records feedback or questions that need follow-up.

The demonstration video is shared separately.

## Project

```text
business_bot/
├── me/
│   ├── about_business.pdf
│   ├── business_summary.txt
│   └── summary.txt
├── business_agent.ipynb
├── agent.py
├── app.py
├── .env.example
└── requirements.txt
```

The notebook contains the persona, operational instructions, router, tool definitions,
agent loop, and Gradio interface. `agent.py` provides the same implementation for the
standalone app. The two summary filenames cover the names used in the assignment.

## Implementation

Messages are routed as general enquiries, leads, or feedback. The model receives the
business documents and conversation history. Requested tools run locally, and their
results are returned to the model before its final reply. Gemini is accessed through
the OpenAI Python SDK's Chat Completions interface.

| Tool | Parameters | Result |
|---|---|---|
| `record_customer_interest` | `email`, `name`, `message` | Saves customer contact details and project notes |
| `record_feedback` | `question` | Saves feedback or an unanswered question |

Both tools return `{"ok": true, "record_id": "..."}` on success or
`{"ok": false, "error": "..."}` on failure. Their JSON schemas are defined in the
notebook and `agent.py`. Records are printed and saved under `logs/`.

The reflection pass checks each draft against the business information and agent
instructions. Its original draft and revised response are saved in `reflection.jsonl`.

## Run

```bash
cd business_bot
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`, then start the app:

```bash
python app.py
```

The interface opens at `http://127.0.0.1:7860`. The notebook can also be run in Jupyter
or Colab with the project files present. API keys and runtime logs are excluded from
the repository. Reflection can be disabled with `ENABLE_REFLECTION=false`.
