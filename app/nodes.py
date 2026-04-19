from langchain_groq import ChatGroq
from app.state import State
from dotenv import load_dotenv
import os

load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile")

SYSTEM_PROMPT = """
You are a polymarketing assistant. You help with:
- SEO strategies
- Content marketing
- Social media marketing
- Email marketing
- Paid ads (Google, Meta)

Only answer marketing-related questions. 
If asked anything outside marketing, politely decline.
"""

# --- GUARDRAIL NODE ---
BLOCKED_TOPICS = [
    "weapon", "hack", "illegal", "drug",
    "violence", "porn", "kill"
]


def guardrail_node(state: State):
    """checks if last message is safe."""
    last_message = state["messages"][-1].content.lower()

    for topic in BLOCKED_TOPICS:
        if topic in last_message:
            from langchain_core.messages import AIMessage
            return {
                "messages": [AIMessage(
                    content="I can only help with marketing topics. Please ask something related to marketing."
                )]
            }

        return state

    # Assistant Node


def assistant_node(state: State):
    """Calls Groq LLM with full conversation history."""
    from langchain_core.messages import SystemMessage

    messages = [SystemMessage(content=SYSTEM_PROMPT)]+state["messages"]
    response = llm.invoke(messages)

    return {"messages": [response]}
