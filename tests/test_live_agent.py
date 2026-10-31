"""
tests/test_live_agent.py
------------------------
Live test of Cognify tutor agent with Gemini API and real-time streaming logging.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Enable debug logging so we see API requests and retries in real time
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Ensure environment variables (GOOGLE_API_KEY) are loaded
for env_path in [
    Path("hello_agent/.env"),
    Path(".env"),
]:
    if env_path.exists():
        load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    print(f"✓ Google/Gemini API Key detected (Length: {len(api_key)})")
else:
    sys.exit("❌ No GOOGLE_API_KEY found in hello_agent/.env or .env")

from agents.tutor.agent import cognify_agent
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

# Learner ID tested in Bruno
LEARNER_ID = "00640701-425e-4d1c-b79e-8086530642cb"

print(f"✓ Loaded agent: {cognify_agent.name} (model: {cognify_agent.model})")
print(f"✓ Registered tools ({len(cognify_agent.tools)}): {[t.__name__ for t in cognify_agent.tools]}")

async def test_live():
    print("\n--- Initializing Session & Runner ---")
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="educentriks_cognify",
        user_id="test_user",
        session_id="session_001"
    )
    print(f"✓ Session created: {session.id}")

    runner = Runner(
        agent=cognify_agent,
        session_service=session_service,
        app_name="educentriks_cognify",
    )

    test_prompt = (
        f"Hello! I am learner with ID {LEARNER_ID}. "
        "Can you look up my profile using your tool and tell me what my name, current role, and target certification are?"
    )
    print(f"\nSending prompt to Gemini ({cognify_agent.model}):")
    print(f"> '{test_prompt}'\n")

    content = Content(parts=[Part(text=test_prompt)])

    event_count = 0
    async for event in runner.run_async(
        user_id="test_user",
        session_id="session_001",
        new_message=content,
    ):
        event_count += 1
        # Print event details
        print(f"\n[Event #{event_count} received: {type(event).__name__}]")
        
        # Check event content
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(f"Tutor: {part.text}")
                if getattr(part, "function_call", None):
                    fc = part.function_call
                    print(f"🔧 [Tool Call]: {fc.name}({fc.args})")
                if getattr(part, "function_response", None):
                    fr = part.function_response
                    print(f"📋 [Tool Result]: {fr.name} -> {fr.response}")

    print("\n" + "=" * 60)
    print(f"LIVE AGENT TEST COMPLETED! (Total events: {event_count})")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_live())
