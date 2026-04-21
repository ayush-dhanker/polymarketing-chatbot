import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer():
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    return SqliteSaver(conn)
