# LangGraph Chatbot with Memory

A stateful chatbot built with LangGraph that maintains conversation memory using Pinecone vector database.

## Features
- **Persistent Memory**: Stores and retrieves conversation history using Pinecone
- **Smart Routing**: Automatically decides when to retrieve past memories
- **State Management**: Uses LangGraph's built-in checkpointing for conversation state
- **FastAPI Integration**: RESTful API with simple chat endpoint

## Quick Start
Install dependencies: `pip install -r requirements.txt` | Set environment variables: `OPENAI_API_KEY`, `PINECONE_API_KEY` | Run: `python api.py` | Chat at: `POST localhost:8000/chat` 