from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="An AI assistant that helps users solve problems.",
    instruction="""
    You are a helpful AI assistant.

    Your responsibilities:
    1. Understand the user's request carefully.
    2. Give accurate and practical answers.
    3. Break complex tasks into smaller steps.
    4. Ask clarifying questions when necessary.
    5. Never invent facts or claim to have completed
       actions that you have not performed.
    """,
)
