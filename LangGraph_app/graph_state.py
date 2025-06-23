from typing import List, TypedDict
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The list of messages that make up the conversation.
        user_id: The unique identifier for the user.
        retrieved_memories: A list of relevant memories retrieved from Pinecone.
    """
    # The 'add_messages' function is a helper utility provided by LangGraph.
    # It ensures that new messages are always added to the existing list
    # of messages in the state, rather than replacing them.
    messages: Annotated[list, add_messages]
    
    user_id: str
    retrieved_memories: List[str]