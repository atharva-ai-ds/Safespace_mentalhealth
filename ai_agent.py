"""LangGraph workflow coordinating intent routing, retrieval, tools, and memory."""
from __future__ import annotations

import logging
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend.config import CHAT_MODEL, OLLAMA_BASE_URL
from backend.intent_classifier import Intent, classify_intent
from backend.memory import memory
from backend.prompts import CRISIS_RESPONSE, GENERAL_SYSTEM_PROMPT, RAG_SYSTEM_PROMPT
from backend.rag import RAGError, retrieve, source_metadata
from backend.tools import call_emergency, find_nearby_therapists

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    sources: list[dict[str, object]]
    tool_called: str


def _latest_message(state: AgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def _llm() -> ChatOllama:
    return ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)


def classify(state: AgentState) -> AgentState:
    return {"intent": classify_intent(_latest_message(state)).value, "sources": [], "tool_called": "None"}


def route(state: AgentState) -> str:
    return state["intent"]


def general_chat(state: AgentState) -> AgentState:
    try:
        response = _llm().invoke([SystemMessage(content=GENERAL_SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [AIMessage(content=str(response.content))]}
    except Exception:
        logger.exception("Ollama unavailable")
        return {"messages": [AIMessage(content="I'm having trouble connecting to my local language model. Please make sure Ollama is running and try again.")]}


def mental_health(state: AgentState) -> AgentState:
    question = _latest_message(state)
    try:
        documents = retrieve(question)
        if not documents:
            return {"messages": [AIMessage(content="I don't have enough verified information to answer that.")], "sources": []}
        context = "\n\n".join(
            f"[{doc.metadata.get('source', 'Document')}, p. {int(doc.metadata.get('page', 0)) + 1}]\n{doc.page_content}"
            for doc in documents
        )
        response = _llm().invoke([SystemMessage(content=RAG_SYSTEM_PROMPT.format(context=context)), HumanMessage(content=question)])
        return {"messages": [AIMessage(content=str(response.content))], "sources": source_metadata(documents)}
    except RAGError:
        logger.exception("RAG unavailable")
        return {"messages": [AIMessage(content="I don't have enough verified information to answer that.")], "sources": []}
    except Exception:
        logger.exception("Mental-health response failure")
        return {"messages": [AIMessage(content="I don't have enough verified information to answer that.")], "sources": []}


def crisis(state: AgentState) -> AgentState:
    result = call_emergency(_latest_message(state))
    logger.warning("Crisis intent detected; emergency tool result: %s", result)
    return {"messages": [AIMessage(content=f"{CRISIS_RESPONSE}\n\n{result}")], "tool_called": "call_emergency"}


def therapist_search(state: AgentState) -> AgentState:
    location = _latest_message(state)
    therapists = find_nearby_therapists(location)
    lines = "\n".join(f"- {item['name']} ({item['location']}): {item['phone']}" for item in therapists)
    return {"messages": [AIMessage(content=f"Here are placeholder local options. Please verify availability and credentials before booking:\n{lines}")], "tool_called": "find_nearby_therapists"}


def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify)
    workflow.add_node("general_chat", general_chat)
    workflow.add_node("mental_health", mental_health)
    workflow.add_node("crisis", crisis)
    workflow.add_node("therapist_search", therapist_search)
    workflow.add_edge(START, "classify")
    workflow.add_conditional_edges("classify", route, {
        Intent.GENERAL_CHAT.value: "general_chat", Intent.MENTAL_HEALTH.value: "mental_health",
        Intent.SUICIDE.value: "crisis", Intent.THERAPIST_SEARCH.value: "therapist_search",
    })
    for node in ("general_chat", "mental_health", "crisis", "therapist_search"):
        workflow.add_edge(node, END)
    return workflow.compile(checkpointer=memory)


graph = create_graph()


def ask_agent(message: str, thread_id: str) -> dict[str, object]:
    result = graph.invoke({"messages": [HumanMessage(content=message)]}, config={"configurable": {"thread_id": thread_id}})
    answer = next((str(item.content) for item in reversed(result["messages"]) if isinstance(item, AIMessage)), "I couldn't generate a response.")
    return {"response": answer, "sources": result.get("sources", []), "tool_called": result.get("tool_called", "None")}
