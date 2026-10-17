# Validation record

Verified on 17 October 2026.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | 16 tests passed |
| Notebook Python cells | 13 executed successfully; fresh API and UI switches disabled |
| Notebook evidence | Offline fixture labelled separately from captured live Gemini transcript |
| Business PDF | Two pages, rendered and visually inspected |
| Runtime packages | openai 3.33.0, gradio 6.30.0, python-dotenv 1.2.4, pypdf 6.10.0 |
| Live model | `gemini-3.1-flash-lite` through the Gemini API's OpenAI-compatible endpoint |
| Browser interface | Gradio app exercised in headless Chrome |
| Live scenarios | Six completed turns: services, pending lead, completed lead, feedback, unknown SLA, pricing |
| Lead tool | Real model request saved Sam Demo, sam@example.com, and project notes |
| Feedback tool | Real model requests saved feedback and the unanswered SLA question |
| Router | General, lead, feedback, and general-to-feedback escalation observed |
| Reflection | Original draft and revised answer captured; compliant drafts may remain unchanged |
| Video QA | A 100-second reference capture was checked locally; your own final video remains to be recorded and is excluded from this upload |

The tests cover grounded source loading, three routes, pending-contact handling,
validation, persistence, real SDK HTTP serialization against a local stub, tool-result
return, short-term history, malformed calls, invented contact rejection, duplicate
protection, bounded loops, disk failure, reflection revision/failure, missing keys,
and provider request pacing. Test fixtures are not presented as live-model evidence.

Live evidence uses synthetic contact details and is in `examples/live_verification/`.
The local reference capture and included evidence came from the production Gradio path, not offline mode. The reference video is not part of the submitted files.
The free project initially reached the 3.8 Flash daily quota, so the final default and
successful captured run use 3.1 Flash-Lite. A 13-second minimum request interval reduces
per-minute quota pressure. Availability and quotas remain provider-controlled; no
paid fallback or billing upgrade is performed.

The archive builder uses an explicit file allowlist and rejects included bytes that
contain the configured API key. `.env`, private runtime logs, caches, and the local
virtual environment are excluded. The optional Hugging Face Space was not deployed.
