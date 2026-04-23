from typing import List, TypedDict
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from tavily import TavilyClient
import sqlite3
from prompts import CON_PROMPT, FINAL_PROMPT, FOR_PROMPT, SYS_PROMPT

load_dotenv()


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}

#clean this function the os environ vars should be set from the .env file in the local folder,confirm if load_dotenv invokes that
def configure_langsmith_tracing() -> bool:
    """
    Enable LangSmith tracing when LANGSMITH_TRACING is truthy.
    """
    tracing_enabled = _is_truthy(os.getenv("LANGSMITH_TRACING"))
    if not tracing_enabled:
        return False

    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print(
            "LangSmith tracing requested but LANGSMITH_API_KEY is missing; "
            "tracing will remain disabled."
        )
        return False

    project_name = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or "consensusgraph"
    # Keep both names for compatibility across LangChain versions.
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", project_name)
    os.environ.setdefault("LANGCHAIN_PROJECT", project_name)
    # Avoid blocking model responses while trace data uploads.
    os.environ.setdefault("LANGCHAIN_CALLBACKS_BACKGROUND", "true")
    return True


LANGSMITH_TRACING_ENABLED = configure_langsmith_tracing()

#replace with sqlite connection
conn = sqlite3.connect('consensusgraph.db', check_same_thread=False)
memory = SqliteSaver(conn)
#separate this concern
model_name = "moonshotai/kimi-k2.6"
model = ChatOpenRouter(model=model_name, temperature=0.1, max_retries=1)
TAVILY_KEY = os.getenv("TAVILY_API_KEY") or os.getenv("TAVILY_SEARCH_KEY")
if not TAVILY_KEY:
    raise RuntimeError(
        "Missing Tavily key. Set TAVILY_API_KEY or TAVILY_SEARCH_KEY in your environment."
    )
tavily = TavilyClient(api_key=TAVILY_KEY)


class AgentState(TypedDict):
    content: str
    pro: str
    con: str
    pro_search_topics: List[str]
    con_search_topics: List[str]
    pro_argument: str
    con_argument: str
    final_answer: str

def _run_tavily_search(topics: List[str], max_results: int = 2) -> List[str]:
    results: List[str] = []
    for topic in topics:
        search_resp = tavily.search(query=topic, max_results=max_results)
        for item in search_resp.get("results", []):
            content = item.get("content")
            if content:
                results.append(content)
    return results

class Procon(BaseModel):
    """Planner output containing prompts + search directions."""

    pro: str = Field(description="prompt for the pro argument")
    pro_search_topics: List[str] = Field(description="search topics for the pro argument")
    con: str = Field(description="prompt for the con argument")
    con_search_topics: List[str] = Field(description="search topics for the con argument")


def planner_node(state: AgentState):
    messages = [
        SystemMessage(content=SYS_PROMPT),
        HumanMessage(content=state["content"]),
    ]
    response = model.with_structured_output(Procon).invoke(messages)
    return {
        "pro": response.pro,
        "con": response.con,
        "pro_search_topics": response.pro_search_topics,
        "con_search_topics": response.con_search_topics,
    }

def for_node(state: AgentState):
    results = _run_tavily_search(state.get("pro_search_topics", []))
    messages = [
        SystemMessage(
            content=FOR_PROMPT.format(
                prompt=state["pro"], task=state["content"], search_results=results
            )
        )
    ]
    response = model.invoke(messages)
    return {"pro_argument": response.content}


def con_node(state: AgentState):
    results = _run_tavily_search(state.get("con_search_topics", []))
    messages = [
        SystemMessage(
            content=CON_PROMPT.format(
                prompt=state["con"], task=state["content"], search_results=results
            )
        )
    ]
    response = model.invoke(messages)
    return {"con_argument": response.content}


def orchestrator_node(state: AgentState):
    messages = [
        SystemMessage(
            content=FINAL_PROMPT.format(
                task=state["content"],
                pro_argument=state["pro_argument"],
                con_argument=state["con_argument"],
            )
        )
    ]
    response = model.invoke(messages)
    return {"final_answer": response.content}


graph_builder = StateGraph(AgentState)
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("for_node", for_node)
graph_builder.add_node("con_node", con_node)
graph_builder.add_node("orchestrator", orchestrator_node)

graph_builder.set_entry_point("planner")
graph_builder.add_edge("planner", "for_node")
graph_builder.add_edge("planner", "con_node")
graph_builder.add_edge("for_node", "orchestrator")
graph_builder.add_edge("con_node", "orchestrator")
graph_builder.add_edge("orchestrator", END)

graph = graph_builder.compile(checkpointer=memory)




#clean up the default prompt and make the invocation a lot more cleaner
if __name__ == "__main__":
    task = input("Enter the debate topic/task: ").strip()
    if not task:
        task = "Should schools ban smartphones in classrooms?"
    if LANGSMITH_TRACING_ENABLED:
        print(
            f"LangSmith tracing: ON (project={os.getenv('LANGSMITH_PROJECT')}). "
            "View traces at https://smith.langchain.com/"
        )
    else:
        print(
            "LangSmith tracing: OFF. Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY "
            "to capture traces."
        )
    run_config = {
        "configurable": {
            "thread_id": "1"
        },
        "metadata": {"model": model_name, "langsmith_tracing": LANGSMITH_TRACING_ENABLED},
        "tags": ["langsmith:nostream"],
    }
    result = graph.invoke({"content": task}, config=run_config)
    print(result["final_answer"])
