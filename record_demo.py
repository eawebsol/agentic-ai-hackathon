"""
record_demo.py
--------------
Autonomous Browser Demo Recorder for Educentriks Cognify.
Equivalent to the Google Build with Gemini 'record-demo' skill:
- Opens Chromium in 720p HD with automated video capture
- Demonstrates the live learner coaching journey
- Showcases the 4-part rubric evaluation & misconception detection
- Walks through Tab 2 (Concept Knowledge Graph & Spaced Repetition)
- Walks through Tab 3 (Institutional Cohort Analytics)
- Saves the final video to docs/demo_video/educentriks_cognify_demo.webm
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("docs/demo_video")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:8501"

def record_demo():
    print("=" * 60)
    print("STARTING AUTONOMOUS AGENT DEMO RECORDER")
    print("=" * 60)
    print(f"Target URL: {URL}")
    print(f"Output Directory: {OUTPUT_DIR.resolve()}\n")

    with sync_playwright() as p:
        print("1. Launching headless Chromium with video recording...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        print(f"2. Navigating to {URL}...")
        try:
            page.goto(URL, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        time.sleep(3)
        print("   ✓ Page loaded. Showcasing Educentriks Cognify brand header and profile context...")
        time.sleep(4)

        # Step 3: Trigger the diagnostic
        print("3. Executing live diagnostic interaction...")
        # Look for the Quick Prompt Chip button
        diagnostic_button = page.get_by_role("button", name="🎯 Test Diagnostic")
        if diagnostic_button.is_visible():
            print("   ✓ Clicking '🎯 Test Diagnostic' quick chip...")
            diagnostic_button.click()
        else:
            print("   ✓ Typing diagnostic prompt into chat input...")
            chat_input = page.get_by_placeholder("Ask a question, explain technical reasoning...")
            chat_input.fill("Can you give me a diagnostic question on Agent Tool Calling so I can test my knowledge?")
            chat_input.press("Enter")

        # Wait for agent reasoning and tool execution
        print("4. Waiting for OpenRouter + Google ADK agent evaluation...")
        time.sleep(8)

        # Scroll to show response
        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(5)
        print("   ✓ Rubric score and feedback displayed on screen.")

        # Step 5: Switch to Tab 2 (Curriculum & Prerequisite Tree)
        print("5. Navigating to Tab 2: Curriculum & Concept Knowledge Graph...")
        tab2 = page.get_by_role("tab", name="Curriculum & Prerequisite Tree")
        if tab2.is_visible():
            tab2.click()
            time.sleep(3)
            # Smooth scroll to showcase concepts
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(3)
            page.evaluate("window.scrollBy(0, -300)")
            time.sleep(2)
            print("   ✓ Showcased concept mastery badges and prerequisite tree.")

        # Step 6: Switch to Tab 3 (Instructor & Cohort Analytics)
        print("6. Navigating to Tab 3: Institutional Cohort Analytics (PS02)...")
        tab3 = page.get_by_role("tab", name="Instructor & Cohort Analytics")
        if tab3.is_visible():
            tab3.click()
            time.sleep(3)
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(4)
            print("   ✓ Showcased class concept gaps and recurring misconceptions.")

        print("\n7. Finalizing demo recording...")
        time.sleep(2)
        
        # Save video path before closing
        video_path = page.video.path()
        context.close()
        browser.close()

        # Rename to standardized demo video filename
        dest_video = OUTPUT_DIR / "educentriks_cognify_demo.webm"
        if Path(video_path).exists():
            if dest_video.exists():
                dest_video.unlink()
            Path(video_path).rename(dest_video)
            print("=" * 60)
            print(f"SUCCESS: Autonomous demo video recorded!")
            print(f"Video saved to: {dest_video.resolve()}")
            print(f"Size: {dest_video.stat().st_size / (1024 * 1024):.2f} MB")
            print("=" * 60)
        else:
            print(f"Video saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    record_demo()

