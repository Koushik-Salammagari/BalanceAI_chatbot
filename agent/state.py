from typing import TypedDict, Annotated, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State schema for the agent.
    Tracks messages and intermediate results.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]