from langgraph.graph import StateGraph, START, END
from app.state import State
from app.nodes import guardrail_node, assistant_node


def should_continue(state: State):
    last_message = state["messages"][-1]

    if last_message.type == "ai":
        return END
    return "assistant"


def build_graph(checkpointer=None):
    graph = StateGraph(State)

    graph.add_node("guardrail", guardrail_node)
    graph.add_node("assistant", assistant_node)

    graph.add_edge(START, "guardrail")
    graph.add_conditional_edges("guardrail", should_continue)
    graph.add_edge("assistant", END)

    return graph.compile(checkpointer=checkpointer)
