# C3 - Agent-Powered Business Assistant

EECE 503P/798S - CedarLoop Studio (fictional business), represented by Mira.

The project is under **`business_bot/`**, matching the assignment's folder structure.

```text
business_bot/
  me/
    about_business.pdf
    business_summary.txt
    summary.txt
  business_agent.ipynb
  app.py
  .env.example
  requirements.txt
  agent.py
  tool_schemas.json
  tests/
  examples/live_verification/
  README.md
  VIDEO_SCRIPT.md
  SUBMISSION_STATUS.md
```

The API key belongs in a local `business_bot/.env` and is intentionally not uploaded.
Both summary filenames are supplied to cover the naming difference in the brief.

## Run

```bash
cd business_bot
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, add your free-tier Gemini key, then run `python app.py`.
See the [full setup guide](business_bot/README.md).

## Required deliverables

- [Business PDF](business_bot/me/about_business.pdf) and [summary](business_bot/me/business_summary.txt).
- [Executed notebook](business_bot/business_agent.ipynb) with separate persona/instructions, router, tools, model interaction, and Gradio.
- Two model-requested tools, documented [schemas](business_bot/tool_schemas.json), and [real synthetic test evidence](business_bot/examples/live_verification/).
- 16 passing automated checks and a verified reflection bonus with original and revised replies.
- [Requirement-by-requirement audit](business_bot/ASSIGNMENT_AUDIT.md) and [validation record](business_bot/VALIDATION.md).

## Final video: to be recorded by the student

The code and documents are ready. **The final demonstration video is still required.**
Follow the [recording guide](business_bot/VIDEO_SCRIPT.md), record the real app yourself,
and add the video at `business_bot/media/live_demo.mp4` or provide an accessible video
link here. Then submit this repository URL and the video to the course.

The assistant's reference recording is excluded from this repository. Hugging Face
Spaces deployment is an optional bonus and has not been performed.
