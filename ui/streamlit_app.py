
from langchain_core.messages import HumanMessage
import uuid
import streamlit as st
import sys
import os

# Add project root to path so 'app' module is found
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

from app.graph import build_graph

st.set_page_config(
    page_title="PolyMarketing Assistant",
    page_icon="📈",
    layout="wide"
)

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rewound" not in st.session_state:
    st.session_state.rewound = False


def get_config():
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def chat(user_input, config=None):
    if config is None:
        config = get_config()

    result = st.session_state.graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    return result["messages"][-1].content


with st.sidebar:
    st.title("🕐 Time Travel")
    st.caption("Rewind to any point in your conversation")

    if st.button("🆕 New Conversation"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.rewound = False
        st.rerun()

    st.divider()

    # checkpoint history
    history = list(st.session_state.graph.get_state_history(get_config()))

    if history:
        st.subheader("Checkpoints")
        for i, checkpoint in enumerate(history):
            msg_count = len(checkpoint.values.get("messages", []))
            if msg_count == 0:
                continue

            # last message preview
            last_msg = checkpoint.values["messages"][-1]
            preview = last_msg.content[:40] + \
                "..." if len(last_msg.content) > 40 else last_msg.content
            label = f"💬 {msg_count} msgs — {preview}"

            if st.button(label, key=f"checkpoint_{i}"):
                st.session_state.rewind_config = checkpoint.config
                st.session_state.rewound = True
                st.rerun()
    else:
        st.caption("No checkpoints yet. Start chatting!")

st.title("📈 PolyMarketing Assistant")
st.caption(
    "Your AI assistant for SEO, content, social media, email & ads marketing")

if st.session_state.rewound:
    st.warning(
        "⏪ You rewound to a previous state. Your next message will branch from here.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask me anything about marketing..."):

    # user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # rewind config or normal
    config = st.session_state.get(
        "rewind_config", None) if st.session_state.rewound else None

    # response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat(user_input, config=config)
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response})

    # Reset rewind state after use
    if st.session_state.rewound:
        st.session_state.rewound = False
        st.session_state.rewind_config = None
