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
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage
from app.state import State
from dotenv import load_dotenv

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

# --- HARD BLOCK: harmful keywords ---
BLOCKED_TOPICS = [
    "weapon", "hack", "illegal", "drug",
    "violence", "porn", "kill"
]

# --- SOFT BLOCK: off-topic LLM classifier ---
MARKETING_CHECK_PROMPT = """
You are a topic classifier.
Decide if the user message is related to marketing.
Marketing includes: SEO, content marketing, social media,
email marketing, paid ads, branding, copywriting, analytics.

Reply with ONLY one word: YES or NO.

User message: {message}
"""


def guardrail_node(state: State):
    """Checks if last message is safe and on-topic."""
    last_message = state["messages"][-1].content.lower()

    # 1. Hard block — harmful keywords
    for topic in BLOCKED_TOPICS:
        if topic in last_message:
            return {
                "messages": [AIMessage(
                    content="⚠️ I can only help with marketing topics. Please ask something related to marketing."
                )]
            }

    # 2. Soft block — off-topic via LLM classifier
    check = llm.invoke(
        MARKETING_CHECK_PROMPT.format(message=last_message)
    )
    is_marketing = check.content.strip().upper()

    if is_marketing == "NO":
        return {
            "messages": [AIMessage(
                content="🎯 I'm a marketing assistant! I can help with SEO, content, social media, email marketing, and paid ads. What marketing challenge can I help you with?"
            )]
        }

    return state  # safe — pass through to assistant


def assistant_node(state: State):
    """Calls Groq LLM with full conversation history."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}