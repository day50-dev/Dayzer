from fastmcp import FastMCP
from typing import List
import random

mcp = FastMCP("ContextSearchMCP")

# Simulated conversation threads
FAKE_DB = {
    "user123": {
        "LLM Proxy Design": [
            {"id": "thread1", "summary": "Discussed initial architecture of proxy"},
            {"id": "thread2", "summary": "Explored performance optimizations"}
        ],
        "Git-backed Threads": [
            {"id": "thread3", "summary": "Talked about versioning chat logs with git"}
        ]
    }
}

THREAD_CONTENT = {
    "thread1": "Conversation log about building a basic proxy with auth/token relay...",
    "thread2": "Conversation log discussing FastAPI performance tuning...",
    "thread3": "Log about designing a git-backed history system..."
}

@mcp.tool()
def list_topics(user_id: str) -> List[str]:
    """
    Lists available conversation topics for the user.
    """
    return list(FAKE_DB.get(user_id, {}).keys())

@mcp.tool()
def get_thread_summary(user_id: str, topic: str) -> str:
    """
    Returns a brief summary of threads matching the topic.
    """
    threads = FAKE_DB.get(user_id, {}).get(topic, [])
    if not threads:
        return f"No threads found for topic '{topic}'."
    summary_list = [f"{i+1}. {t['summary']} (id: {t['id']})" for i, t in enumerate(threads)]
    return "\n".join(summary_list)

@mcp.tool()
def get_thread_content(user_id: str, thread_id: str) -> str:
    """
    Retrieves full content of a specific thread by ID.
    """
    return THREAD_CONTENT.get(thread_id, "Thread not found.")

if __name__ == "__main__":
    mcp.run()

