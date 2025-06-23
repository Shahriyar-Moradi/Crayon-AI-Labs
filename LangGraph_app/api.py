import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import uvicorn
# from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage

from graph_state import GraphState
from langGraph_agent import (
    store_message_node,
    retrieve_memories_node,
    generate_response_node,
    should_retrieve_router,
)
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

load_dotenv()

# For the tutorial, we'll use an in-memory checkpointer.
# For production, you would use a persistent checkpointer like SqliteSaver.
# memory = MemorySaver()
# memory = SqliteSaver.from_conn_string("memory.db")

# --- Build the Graph ---
workflow = StateGraph(GraphState)
workflow.add_node("store_message", store_message_node)
workflow.add_node("retrieve", retrieve_memories_node)
workflow.add_node("generate", generate_response_node)
workflow.set_entry_point("store_message")
workflow.add_edge("retrieve", "generate")
workflow.add_conditional_edges(
    "store_message",
    should_retrieve_router,
    {"retrieve": "retrieve", "generate": "generate"},
)
workflow.add_edge("generate", END)

# COMPILE THE GRAPH WITH THE CHECKPOINTER
app_graph = workflow.compile(checkpointer=memory)


# --- FastAPI App ---
app = FastAPI()

# The request no longer needs to include the chat history
class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # The config now uses the user_id as the thread_id for the checkpointer
    config = {"configurable": {"thread_id": request.user_id}}

    # The input to the graph is now just the new message
    input_data = {
        "messages": [HumanMessage(content=request.message)],
        "user_id": request.user_id
    }
    
    # Use 'ainvoke' to run the graph with the input and config
    final_state = await app_graph.ainvoke(input_data, config)
    
    # The final response is the last message in the state
    response_message = final_state["messages"][-1].content
    
    return {"response": response_message}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)