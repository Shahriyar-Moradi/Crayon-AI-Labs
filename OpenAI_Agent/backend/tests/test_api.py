"""
Minimal test suite for Memory Chatbot API
Simple and clean tests for core functionality
"""

import pytest
import tempfile
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, get_db, ChatMessage, Base, load_conversation_history, save_message

# Test database setup
@pytest.fixture
def test_db():
    """Create temporary test database"""
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db.close()
    
    test_engine = create_engine(f"sqlite:///{temp_db.name}")
    TestSessionLocal = sessionmaker(bind=test_engine)
    
    Base.metadata.create_all(bind=test_engine)
    
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestSessionLocal()
    
    app.dependency_overrides.clear()
    os.unlink(temp_db.name)

@pytest.fixture
def client(test_db):
    """Test client"""
    return TestClient(app)

# Database Tests
def test_save_and_load_message(test_db):
    """Test saving and loading messages"""
    save_message("test-chat", "User", "Hello", test_db)
    
    history = load_conversation_history("test-chat", test_db)
    
    assert len(history) == 1
    assert history[0] == ("User", "Hello")

def test_empty_conversation_history(test_db):
    """Test empty conversation history"""
    history = load_conversation_history("empty-chat", test_db)
    assert history == []

# API Tests
def test_health_endpoint(client):
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_info_endpoint(client):
    """Test API info"""
    response = client.get("/info")
    assert response.status_code == 200
    assert "Memory Chatbot API" in response.json()["name"]

@patch('api.process_query_with_memory')
@patch('api.memory_service.retrieve_memories')
def test_chat_endpoint(mock_retrieve, mock_process, client):
    """Test chat endpoint"""
    mock_process.return_value = "Hello! How can I help you?"
    mock_retrieve.return_value = []
    
    response = client.post("/chat", json={
        "user_id": "test-user",
        "message": "Hello"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user"
    assert data["message"] == "Hello"
    assert "response" in data

def test_get_chat_history(client, test_db):
    """Test getting chat history"""
    save_message("test-user", "User", "Hello", test_db)
    
    response = client.get("/chat/history/test-user")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user"
    assert len(data["conversation_history"]) == 1

def test_clear_chat_history(client, test_db):
    """Test clearing chat history"""
    save_message("test-user", "User", "Hello", test_db)
    
    response = client.delete("/chat/history/test-user")
    
    assert response.status_code == 200
    
    # Verify history is cleared
    history = load_conversation_history("test-user", test_db)
    assert len(history) == 0

def test_invalid_chat_request(client):
    """Test invalid request"""
    response = client.post("/chat", json={
        "user_id": "",  # Invalid empty user_id
        "message": "Hello"
    })
    
    assert response.status_code == 422 