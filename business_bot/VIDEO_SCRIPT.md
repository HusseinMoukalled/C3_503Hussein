# Final live demonstration: approximately 4-6 minutes

From the repository root, first run `cd business_bot`.

Record the screen with normal `python app.py`, **not** `--offline-demo`.
Keep the API key and any real customer data off screen. Use synthetic contact details.
If the free quota is exhausted, wait and retry rather than replacing live evidence
with a scripted response. This script is a recording guide, not proof of a completed run.

1. **Business identity and prompt (0:00-0:30).** Show `me/about_business.pdf`, the
   summary, and the notebook's separate PERSONA and INSTRUCTIONS cells. Explain:
   "Mira represents CedarLoop Studio. Both PDF text and the short summary are included
   in the system prompt. Prices and unsupported business claims cannot be invented."
2. **General route (0:30-0:50).** Ask: "What services do you offer?" Show the answer
   and the router event `general` in the terminal or `events.jsonl`.
3. **Multi-turn lead route (0:50-1:30).** Ask: "I'd like a consultation for a bakery FAQ
   bot." Show Mira requesting missing contact details and the absence of a premature
   lead record. Reply: "My name is Sam Demo and my email is sam@example.com. Please
   save my details for follow-up about the bakery FAQ bot." Show the model's tool
   event, the saved lead (name, email, notes), and the final acknowledgement.
4. **Feedback route (1:30-1:50).** Ask: "Feedback: your onboarding instructions were
   confusing." Show `record_feedback` and the resulting JSONL entry.
5. **Unknown question (1:50-2:15).** Ask: "Do you offer a guaranteed 24/7 response
   SLA?" Show that Mira acknowledges the gap and saves the question. Show the
   general-to-feedback escalation event and the new feedback record.
6. **Reflection bonus (2:15-2:40).** Show a `reflection.jsonl` entry with `draft`,
   `revised`, and `changed`. An unchanged compliant answer is valid. Explain that
   the second model call checks grounding, contact collection, and logging claims.
   Do not manufacture a live mistake to imply the model spontaneously made one.
   The offline fixture separately includes a deliberately flawed pricing draft
   to test revision; label it clearly if you show it.
7. **Code and delivery (2:40-3:00).** Show the two schemas, model-tool-result loop,
   notebook, and passing offline tests. Mention Gemini free-tier quota and the
   ignored `.env`. Finish with the GitHub URL and, if completed, the Space URL.

Optional automated capture, after starting the live app:

```powershell
python record_demo.py --url http://127.0.0.1:7860 --output media/live_demo.mp4
```

The helper captures actual browser frames with scene captions and real app replies.
It has no narration. Supplement it with your own explanation of the notebook and logs
if the instructor expects a narrated presentation. Watch the result before submitting.

After recording, add your video at `business_bot/media/live_demo.mp4` in the repository, or add an accessible video link to the root README. Free-tier replies are paced; you may pause or trim waiting time while keeping the actual requests and results visible.
