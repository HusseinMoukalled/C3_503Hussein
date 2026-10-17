"""Capture actual Gradio browser states to a captioned MP4 walkthrough.

Start app.py first. Default is a live capture; --offline explicitly labels fixtures.
This helper records screen states, with held frames for readability, not a real-time
screen video. It never generates simulated live replies.
"""
import argparse
import html
import io
import json
import time
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:7860")
    parser.add_argument("--output", default="media/live_demo.mp4")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--log-dir")
    args = parser.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    logs = Path(args.log_dir or ("logs/offline_demo" if args.offline else "logs"))
    baseline = {}
    for name in ["events.jsonl", "leads.jsonl", "feedback.jsonl", "reflection.jsonl"]:
        path = logs / name
        baseline[name] = len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0
    mode = "OFFLINE FIXTURE - NO LIVE MODEL" if args.offline else "LIVE GEMINI - ACTUAL APP REPLIES"
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    except OSError:
        font = small = ImageFont.load_default()
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 820}, device_scale_factor=1)
        page.goto(args.url, wait_until="domcontentloaded")
        page.locator("textarea").first.wait_for(timeout=60000)
        is_offline = "OFFLINE VERIFICATION DEMO" in page.inner_text("body")
        if is_offline != args.offline:
            raise RuntimeError("Capture mode does not match the app. Use --offline only for app.py --offline-demo.")
        with imageio.get_writer(str(target), fps=10, codec="libx264", quality=8,
                                macro_block_size=1, ffmpeg_log_level="error") as writer:
            def capture(caption, seconds=8):
                frame = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
                canvas = Image.new("RGB", (1280, 928), "#153c3a")
                canvas.paste(frame, (0, 0))
                draw = ImageDraw.Draw(canvas)
                draw.text((22, 834), mode, fill="#abebcf", font=font)
                draw.text((22, 864), caption, fill="white", font=font)
                draw.text((22, 898), "Actual browser-state capture; frames held for readability. Synthetic contact details.",
                          fill="#bed0cd", font=small)
                pixels = np.asarray(canvas)
                for _ in range(seconds * 10):
                    writer.append_data(pixels)

            capture("CedarLoop Studio: grounded business assistant with routing, tools, and reflection.")
            scenes = [
                ("What services do you offer?", "1. General enquiry: answer from the business PDF and summary."),
                ("I'd like a consultation for a bakery FAQ bot.", "2. Lead route: request missing contact fields before saving."),
                ("My name is Sam Demo and my email is sam@example.com. Please save my details for follow-up about the bakery FAQ bot.",
                 "3. Model-requested lead tool: validate and save name, email, and notes."),
                ("Feedback: your onboarding instructions were confusing.", "4. Feedback route: save the customer's original feedback."),
                ("Do you offer a guaranteed 24/7 response SLA?", "5. Unknown business detail: log the question and acknowledge the gap."),
                ("What is your pricing?", "6. Reflection: check the draft against business facts before replying."),
            ]
            transcript = []
            for message, caption in scenes:
                reflection_path = logs / "reflection.jsonl"
                before_count = len(reflection_path.read_text(encoding="utf-8").splitlines()) if reflection_path.exists() else 0
                textbox = page.locator("textarea").first
                textbox.fill(message)
                textbox.press("Enter")
                # Wait for Gradio's input to re-enable after its processing cycle.
                deadline = time.monotonic() + 180
                while time.monotonic() < deadline:
                    page.wait_for_timeout(500)
                    body = page.inner_text("body")
                    if any(value in body for value in ["Set GEMINI_API_KEY", "quota is currently exhausted", "model service is unavailable", "API key was rejected"]):
                        raise RuntimeError("App reported a configuration or provider failure. Complete live setup before recording.")
                    if reflection_path.exists():
                        rows = reflection_path.read_text(encoding="utf-8").splitlines()
                        if len(rows) > before_count:
                            final_answer = json.loads(rows[-1])["revised"]
                            break
                else:
                    raise RuntimeError("Timed out waiting for a completed reflection. Enable reflection and inspect app logs.")
                page.wait_for_timeout(1000)
                body = page.inner_text("body")
                for failure in ["Set GEMINI_API_KEY", "quota is currently exhausted", "model service is unavailable", "API key was rejected"]:
                    if failure in body:
                        raise RuntimeError("App reported a configuration or provider failure. Complete live setup before recording.")
                capture(caption, 10)
                transcript.append({"user": message, "assistant": final_answer})
                print(caption, flush=True)

            # Render actual saved records and reflection evidence, not invented status text.
            data = {}
            for filename in ["events.jsonl", "leads.jsonl", "feedback.jsonl", "reflection.jsonl"]:
                path = logs / filename
                if path.exists():
                    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                    if filename in baseline:
                        rows = rows[baseline[filename]:]
                    if filename == "events.jsonl":
                        rows = rows[-16:]
                    elif filename == "reflection.jsonl":
                        rows = rows[-1:]
                    data[filename] = rows
            if not data.get("leads.jsonl") or len(data.get("feedback.jsonl", [])) < 2:
                raise RuntimeError("Expected lead, feedback, and unknown-question records were not found. Review the run.")
            if not args.offline:
                evidence = Path("examples/live_verification")
                evidence.mkdir(parents=True, exist_ok=True)
                (evidence / "transcript.json").write_text(json.dumps(transcript, indent=2), encoding="utf-8")
                for filename, rows in data.items():
                    (evidence / filename).write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
                import os
                from datetime import datetime, timezone
                from dotenv import dotenv_values
                config = dotenv_values(".env")
                (evidence / "run_metadata.json").write_text(json.dumps({"mode": "live Gemini API",
                    "model": os.getenv("GEMINI_MODEL") or config.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
                    "captured_at_utc": datetime.now(timezone.utc).isoformat(), "synthetic_contacts_only": True,
                    "capture": "record_demo.py against real Gradio app; held browser frames, not real-time video"}, indent=2), encoding="utf-8")
            markup = "<html><body style='background:#f4f8f6;color:#153c3a;font:16px Arial;padding:30px'>"
            markup += "<h1>Actual saved tool records</h1><p>" + html.escape(mode) + "</p>"
            for filename in ["leads.jsonl", "feedback.jsonl"]:
                markup += "<h2>" + filename + "</h2><pre style='white-space:pre-wrap;font-size:15px'>" + html.escape(json.dumps(data[filename], indent=2)) + "</pre>"
            markup += "</body></html>"
            page.set_content(markup)
            capture("7. Evidence: real JSONL records written by the two local tools.", 12)
            route_rows = "".join("<tr>" + "".join("<td style='padding:9px;border-bottom:1px solid #c3d5ce'>" +
                html.escape(str(row.get(key, ""))) + "</td>" for key in ["event", "intent", "name", "ok"]) + "</tr>"
                for row in data.get("events.jsonl", []))
            page.set_content("<html><body style='background:#f4f8f6;color:#153c3a;font:17px Arial;padding:35px'>"
                             "<h1>Router and tool audit trail</h1><table style='border-collapse:collapse;width:100%'>"
                             "<tr><th>Event</th><th>Intent</th><th>Tool</th><th>OK</th></tr>" + route_rows + "</table></body></html>")
            capture("8. Routing evidence: general, lead, feedback, and unknown-question escalation.", 10)
            page.set_content("<html><body style='background:#f4f8f6;color:#153c3a;font:17px Arial;padding:35px'><h1>Reflection audit log</h1><pre style='white-space:pre-wrap'>" +
                             html.escape(json.dumps(data.get("reflection.jsonl", []), indent=2)) + "</pre><p>draft + revised + changed are logged for inspection.</p></body></html>")
            capture("9. Bonus: the reflection log preserves the original draft and final reply.", 10)
        browser.close()
    print(f"Saved {mode} walkthrough: {target}")


if __name__ == "__main__":
    main()
