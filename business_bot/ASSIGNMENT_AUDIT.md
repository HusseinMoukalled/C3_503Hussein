# Audit against the assignment brief

Checked again against all three pages of **C3 - Introduction to Agents** before the
final GitHub push. The project folder is `business_bot/`, as shown on page 1.

| Requirement from the brief | Location and verification | Status |
|---|---|---|
| Fictional name, mission, services, team, unique value proposition | `me/about_business.pdf` and `me/business_summary.txt`; CedarLoop Studio, its mission, five services, three fictional team members, and bilingual/simple-workflow proposition | Complete |
| Business profile PDF | `me/about_business.pdf`, two readable, rendered and visually checked pages | Complete |
| Short text summary | Canonical `me/business_summary.txt`; `me/summary.txt` and project-root aliases also supplied because the brief uses both filenames | Complete |
| Main notebook | `business_agent.ipynb`, full implementation and 13 successfully executed code cells | Complete |
| Clearly separated persona and instructions | Notebook sections 2 and 3, plus labelled `PERSONA` and `INSTRUCTIONS` constants in `agent.py` | Complete |
| Three-intent router before generation | `route_message` chooses general, lead, or feedback and supplies route-specific handling instructions | Complete |
| Unknown-question handling | General questions missing published details trigger a model-requested feedback tool and a logged route escalation; the live SLA example demonstrates this | Complete |
| `record_customer_interest(email, name, message)` | Required positional fields implemented; validates and writes name, email, and notes; real model invocation captured | Complete |
| `record_feedback(question)` | Saves original feedback/unanswered question; real model invocations captured for both cases | Complete |
| Push/print or file logging | Both tools print records and append JSONL; router and reflection have separate audit logs | Complete |
| MCP-style tool schemas | `tool_schemas.json`, notebook section 4, and README tool table document name, parameters, and expected output | Complete |
| Assemble `system_prompt` | `build_system_prompt` combines persona, instructions, TXT content, and extracted PDF text | Complete |
| Stay in character and avoid invented facts | Operational instructions, grounding sources, validation, and reflection; published custom quoting is used instead of invented prices | Complete |
| Encourage/collect contact information over turns | Live conversation first requests missing fields, then saves supplied Sam Demo / sam@example.com / bakery project notes | Complete |
| Gemini API or OpenAI | Real Gemini API calls via Google's officially documented OpenAI-compatible endpoint | Complete |
| API interface named in the brief | Uses modern `OpenAI(...).chat.completions.create`, the maintained equivalent of the older `openai.ChatCompletion` example; this modernization is explained in README/notebook | Complete |
| Pass input, chat history, and tools | `BusinessAgent.respond` sends the user message, short-term history, system prompt, and both tool definitions | Complete |
| Execute model tool calls and return results | Explicit loop executes registered tools and sends `role=tool` messages with matching `tool_call_id`; verified by tests and real Gemini tool records | Complete |
| Otherwise return generated text | Direct answer path and final answer after tool execution; live service and pricing answers captured | Complete |
| Gradio ChatInterface | `app.py` and notebook section 10; browser interaction verified against the running app | Complete |
| `requirements.txt` | Runtime dependencies included; separate optional development requirements provided | Complete |
| API key in local `.env`, never uploaded | Configured locally and successfully used; `.env.example` is uploaded instead; `.env` excluded from ZIP/Git | Complete |
| Runs successfully | 16 tests passed, 13 notebook cells executed, live browser scenarios and synthetic saved records verified; see `VALIDATION.md` | Complete |
| GitHub repository | Project will be published under `business_bot/` in the supplied `HusseinMoukalled/C3_503Hussein` repository | Included in this push |
| Video showcasing functionality | Student will record the final video; `VIDEO_SCRIPT.md` supplies a scenario-by-scenario guide. The assistant's reference video is excluded | **Remaining student step** |
| Optional reflection bonus | Review pass before final reply, original/revised logs, an actual live revision, plus a labelled offline correction example | Complete |
| Optional Hugging Face Spaces bonus | Configuration and deployment instructions supplied; no hosted Space is claimed | Not deployed; optional |

## Required folder check

```text
business_bot/
  me/
    about_business.pdf
    business_summary.txt
  business_agent.ipynb
  app.py
  .env                 (local only, deliberately absent from Git)
  requirements.txt
```

The additional helper modules, schemas, tests, documentation, aliases, and synthetic
live evidence support these required files. They do not replace any required file.

Before final course submission, record and add your own video (or an accessible video
link) and submit the GitHub repository URL. All required project files are provided;
the course's video requirement remains explicitly pending until you complete it.
