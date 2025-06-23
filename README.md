# Crayon AI Labs - Chatbot Projects

This repository contains two implementations of AI chatbots with memory capabilities, showcasing different approaches and complexity levels.

## 🚀 Project Overview

### Solution 1: Simple LangGraph Application (`/LangGraph_app`)
A streamlined chatbot built with LangGraph that demonstrates basic conversation flow and memory integration.
- **Framework**: LangGraph with FastAPI
- **Memory**: Pinecone vector database for conversation storage
- **Features**: Smart routing, state management, persistent memory
- **API**: Single `/chat` endpoint for message processing
- **Setup**: Simple configuration with environment variables

### Solution 2: Complete OpenAI Agent Solution (`/OpenAI_Agent`)
A full-featured chatbot system with autonomous memory management and advanced agent capabilities.
- **Framework**: OpenAI API with Agent SDK
- **Memory System**: Vector-indexed user messages with autonomous retrieval decisions
- **Intelligence**: AI autonomously decides when to fetch relevant memories for replies
- **Architecture**: Backend API separated from Streamlit frontend
- **Database**: Pinecone vector store for message indexing and retrieval

## 🎯 Memory Functionality
- **Storage**: Every user message automatically stored in vector format
- **Retrieval**: AI makes autonomous decisions on memory fetching relevance
- **Context**: Retrieved memories enhance response quality and continuity
- **Indexing**: Vector-based similarity search for relevant conversation history

## 🏗️ Architecture
- **Backend**: Independent API services (FastAPI/OpenAI Agent SDK)
- **Frontend**: Streamlit web interface for user interaction
- **Database**: Pinecone vector database for scalable memory storage
- **AI Models**: OpenAI GPT models for conversation and decision-making

## 📋 Requirements
- Python , OpenAI API key, Pinecone API key
- Dependencies listed in each project's `requirements.txt`

## 🚀 Quick Start
1. Choose your version (LangGraph_app or OpenAI_Agent)
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables: `OPENAI_API_KEY`, `PINECONE_API_KEY`
4. Run backend API and Streamlit frontend separately

## ☁️ Deployment
The chatbot API is deployed on **Google Cloud Run** as part of the technical challenge implementation.

### Live API Endpoints
- **API Status**: [https://chat-memory-333130950445.europe-west1.run.app/](https://chat-memory-333130950445.europe-west1.run.app/)
- **API Documentation**: [https://chat-memory-333130950445.europe-west1.run.app/docs](https://chat-memory-333130950445.europe-west1.run.app/docs)

### Testing the Deployed API
- Access the interactive API documentation at the `/docs` endpoint
- Test chat functionality with POST requests to `/chat`
- Monitor API status and health through the root endpoint
- Scalable deployment with automatic container management on Cloud Run 