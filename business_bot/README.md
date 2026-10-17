---
title: CedarLoop Studio - Mira
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
python_version: '3.12'
pinned: false
---

# CedarLoop Studio: an agent-powered business assistant

EECE 503P/798S, C3 - Introduction to Agents. All business and team details are fictional.

Mira answers from a PDF and text summary, routes enquiries, gathers leads over multiple
turns, and saves feedback or unanswered questions using model-requested function calls.
An optional second model pass checks each reply and logs its draft and revision.

## Your demonstration video

The project has passed live Gemini verification. A six-turn transcript and synthetic
tool records are in `examples/live_verification/`; scripted notebook examples are
labelled separately. **You will record the final submission video yourself.**
Follow `VIDEO_SCRIPT.md`, show the real Gradio app and notebook, then add your video
as `business_bot/media/live_demo.mp4` in the GitHub repository or provide an accessible
video link. No final submission video is included in this repository yet.

## Free model setup

This project calls the **Gemini API**, using the OpenAI Python client's Chat Completions
interface and Google's officially documented compatibility endpoint. It does not call
OpenRouter or require an OpenAI account. The modern `client.chat.completions.create`
method is the maintained SDK equivalent of the brief's older `openai.ChatCompletion`
example. Real model tool calls are dispatched in `BusinessAgent.respond`; a heuristic
router does not pretend to be the model.

1. Install Python 3.12, open a terminal in this folder, and create a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

   On macOS/Linux, activate with `source .venv/bin/activate` and copy with
   `cp .env.example .env`.

2. Create a free-tier Gemini API key at [Google AI Studio](https://aistudio.google.com/apikey).
   Put it in your local `.env` after `GEMINI_API_KEY=`. Do not upload `.env`.
   Check that your Google project is on the Free tier if you want to avoid paid usage.
   Free access has eligibility, model availability, and quota limits; it is not unlimited.
   The default `gemini-3.1-flash-lite` is listed with free-tier text input/output on the pricing
   page checked on 17 October 2026. Change `GEMINI_MODEL` if your project exposes a
   different compatible model with a free tier.

3. Run:

   ```powershell
   python app.py
   ```

   Open the local address printed by Gradio, usually `http://127.0.0.1:7860`.
   To conserve free quota set `ENABLE_REFLECTION=false`. A normal reply makes one
   generation request; a tool call usually needs an additional request for the final
   reply, and reflection adds another. The observed project quota during testing was
   five requests per minute. Real provider calls are therefore paced at least 13
   seconds apart by default, including reflection. A tool-and-review turn may take
   roughly 30-45 seconds. `MIN_REQUEST_INTERVAL_SECONDS` can be adjusted to match
   your actual project quota. Wait and retry if the provider still returns 429.

## Notebook

Open `business_agent.ipynb` in Jupyter from this folder. It contains the actual agent
implementation, separate PERSONA and INSTRUCTIONS cells, schemas, routing examples,
an offline tool-loop demonstration, and switches for a live Gemini run and Gradio.
The scripted examples are explicitly labelled **offline verification**. A separate
section reads the captured real Gemini transcript from `examples/live_verification/`. Install `requirements-dev.txt` for Jupyter support.

For Colab, upload this whole project folder (including `me/`) or clone your GitHub
repo first, then change the notebook's working directory to the project folder.
Install `requirements.txt` in the Colab environment and set the key using Colab Secrets
or a local `.env`; do not put it in a notebook cell that will be committed. Run the
notebook from the first cell. Set `LAUNCH_GRADIO=True`; the notebook uses a share link
only when running inside Colab.

## Architecture

```text
User + short-term history
  -> heuristic router: general | lead | feedback
  -> route-specific instructions + persona + TXT + extracted PDF
  -> Gemini via OpenAI SDK, with both function schemas
  -> model tool call -> validate -> execute -> return tool result to model
  -> draft answer -> optional reflection -> Gradio reply
```

General questions use the documents. If the answer is absent, the model calls
`record_feedback`; the event log records escalation from general to feedback.
Lead messages collect missing fields instead of prematurely saving incomplete records.
Feedback messages request the feedback tool. Mixed feedback and lead requests may
use both tools. Each tool result is returned with its original `tool_call_id` before
the next generation request. Unknown tools, malformed arguments, invalid email
addresses, and invented contact details are rejected. Repeated identical calls in
one turn reuse their result. The loop stops after five requests.

The router is deliberately small: keyword cues plus the previous assistant's request
for contact details. It can misclassify unusual wording; the model receives full
instructions and can still call the appropriate tool. This is an instructional
prototype, not a production classifier or a complete security boundary.

## Tools and logs

MCP-style `name`, `description`, `inputSchema`, and `outputSchema` definitions are in
`tool_schemas.json` and in the notebook. These are local tools, not an MCP server.

| Function | Required string parameters | Expected output | Side effect |
|---|---|---|---|
| `record_customer_interest` | `email`, `name`, `message` | `{"ok": true, "record_id": "UUID"}` or `{"ok": false, "error": "reason"}` | Append a lead to `logs/leads.jsonl`; print record |
| `record_feedback` | `question` | Same success/error structure | Append to `logs/feedback.jsonl`; print record |

`events.jsonl` records router decisions, escalation, and tool outcomes.
`reflection.jsonl` contains `draft`, `revised`, and `changed` for the bonus step.
These files are created when the corresponding events occur. Tools save records;
they do not send emails, confirm appointments, or automatically contact a human.
Print logging is provided as requested by the assignment. Keep actual customer logs
private; the repository ignores `logs/`. Demonstrations use `sam@example.com`.

## Verification and video

```powershell
python -m unittest discover -s tests -v
python app.py --offline-demo
```

The second command explicitly labels the UI as a **scripted SDK fixture**. The actual
router, validation, orchestration, and file-writing tools execute. No API calls occur.
The offline mode is a development aid and does not satisfy the live-model requirement.

After adding your Gemini key, run the live check and record the final video:

```powershell
python live_check.py
python app.py
```

See `VIDEO_SCRIPT.md` for the recording sequence. `record_demo.py` can automatically
capture the Gradio scenarios to MP4 when a local app is running; its default mode is
**live**, and it refuses to label an offline UI as live. Install `requirements-dev.txt`
and run `python -m playwright install chromium` before using that helper.
Review generated logs and replies before submission: model behavior is probabilistic.

## GitHub submission

The submission repository is [C3_503Hussein](https://github.com/HusseinMoukalled/C3_503Hussein).
Its project files live in `business_bot/`, matching the brief. From the repository root,
run `cd business_bot` before the setup commands above.

To publish the same project to another empty repository, run the following in this
project folder, replacing the remote URL as needed:

```powershell
git init
git add .
git status
git commit -m "Build CedarLoop business assistant"
git branch -M main
git remote add origin https://github.com/HusseinMoukalled/C3_503Hussein.git
git push -u origin main
```

Check that `.env` and `logs/` do not appear in the staged files. Add your final live
video to `media/live_demo.mp4` within this project folder, or put an accessible video link in this README if
the recording exceeds your repository's file-size limit. Submit the GitHub URL and
video link. The supplied project has been exercised with a real Gemini key; the captured evidence
is included. Record your own final demonstration using `VIDEO_SCRIPT.md`. Your own key is still required to run a new
chat session after cloning, because credentials are never published.

## Optional Hugging Face Spaces bonus

Create a Gradio Space and upload the project files at its repository root. This
README already includes the Space configuration. In Space settings add a **secret**
`GEMINI_API_KEY` and variables `GEMINI_MODEL=gemini-3.1-flash-lite`,
`SERVER_NAME=0.0.0.0`, and optionally `ENABLE_REFLECTION=true`.
Never upload `.env`. Ordinary Space disk storage can be reset on restart; use available
persistent storage with `BOT_LOG_DIR` pointing to it if records must survive restarts.
Console print logs still demonstrate the required logging mechanism.
Upload no private customer records. Keep an API-backed demo restricted if you do not
want public visitors to consume your free quota. Actual Space deployment is optional
and is not claimed in the supplied project.

## References

- [Gemini OpenAI compatibility and function calling](https://ai.google.dev/gemini-api/docs/openai)
- [Gemini pricing and free tier](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini billing tiers](https://ai.google.dev/gemini-api/docs/billing)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface)
- [Hugging Face Spaces configuration](https://huggingface.co/docs/hub/en/spaces-config-reference)
