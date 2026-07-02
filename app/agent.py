"""
LangGraph Agent with Production Error Handling
Retry logic, model fallback, and structured state management.
"""

from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langsmith import traceable
from typing_extensions import Annotated, TypedDict

from app.config import get_settings

# === Agent State ===


class AgentState(TypedDict):
    """
    State for Production Agent
    Uses Annoted with add message reducer for message accumulation
    """

    messages: Annotated[list[BaseMessage], add_messages]
    error: Optional[str]
    retry_count: int
    model_used: str


# === Agent Builder ===


class ProductionAgent:
    """
    Production Langraph agent with:
    - Retry on faliure (model fallback)
    - Graceful error handling
    - Langsmith tracing
    """

    # I dont have token available in claud and chatgpt so i have used gemini model

    def __init__(self):
        settings = get_settings()

        self.primary_llm = ChatGoogleGenerativeAI(
            model=settings.primary_model,
            # temperature = 0 can be used if we uses the chatgpt of anthropic models
            timeout=30,
            max_retries=0,  # we handle retries by ourself
            api_key=settings.google_api_key
            
        )

        self.fallback_llm = ChatGoogleGenerativeAI(
            model=settings.fallback_model,
            timeout=30,
            max_retries=0,
            api_key=settings.google_api_key
        )

        self.max_retries = settings.max_retries
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state machine."""

        @traceable(name="process_message")
        def process_message(state: AgentState) -> dict:
            """Try to process the message with the primary modle"""

            try:
                response = self.primary_llm.invoke(state["messages"])
                return {"messages": [response], "error": None, "model_used": "primary"}

            except Exception as e:
                return {
                    "error": str(e),
                    "retry_count": state["retry_count"] + 1,
                    "model_used": "",
                }

        @traceable(name="try_fallback")
        def try_fallback(state: AgentState) -> dict:
            """Fallback to secondary model."""
            try:
                response = self.fallback_llm.invoke(state["messages"])
                return {"messages": [response], "error": None, "model_used": "fallback"}
            except Exception as e:
                return {
                    "error": str(e),
                    "model_used": "",
                }

        @traceable(name="handle_error")
        def handle_error(state: AgentState) -> dict:
            """Return a gracefull error message."""

            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I'm sorry, I'm having a trouble processing your request"
                            "right now. Please try again in a moment."
                        )
                    )
                ],
                "model_used": "error_handler",
            }

        def route_after_process(state: AgentState) -> str:
            """Decide what to do after primary model attempt."""

            if state.get("error") is None:
                return "done"
            elif state["retry_count"] < self.max_retries:
                return "fallback"
            else:
                return "error"

        def route_after_fallback(state: AgentState) -> str:
            """Decide what to do after fallback attempt."""
            if state.get("error") is None:
                return "done"
            else:
                return "error"

        # Build a graph
        graph = StateGraph(AgentState)

        graph.add_node("process", process_message)
        graph.add_node("fallback", try_fallback)
        graph.add_node("error", handle_error)

        graph.add_edge(START, "process")
        graph.add_conditional_edges(
            "process",
            route_after_process,
            {"done": END, "fallback": "fallback", "error": "error"},
        )
        graph.add_conditional_edges(
            "fallback",
            route_after_fallback,
            {"done": END, "error": "error"},
        )
        graph.add_edge("error", END)

        return graph.compile()

    @traceable(name="production_agentic_invoke")
    def invoke(self, message: str) -> dict:
        """
        Invoke the agent with a user message.
        Returns: {"response": str, "model_used": str, "error": str | None}
        """

        result = self.graph.invoke(
            {
                "messages": [HumanMessage(content=message)],
                "error": None,
                "retry_count": 0,
                "model_used": "",
            }
        )

        return {
            "response": result["messages"][-1].content,
            "model_used": result.get("model_used", "unknown"),
            "error": result.get("error"),
        }
