import streamlit as st
import asyncio
import uuid
from typing import List, Tuple
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_agent import process_query_with_memory, memory_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Memory-Enabled AI Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1e88e5;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        border-left: 4px solid #1976d2;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: auto;
        border-left: 4px solid #7b1fa2;
    }
    
    .memory-section {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
    }
    
    .sidebar-section {
        background-color: #fafafa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'user_id_input' not in st.session_state:
        st.session_state.user_id_input = ""

def load_user_conversation(user_id: str):
    """Load conversation history for a specific user ID"""
    try:
        # Get past memories for this user
        memories = memory_service.get_all_user_memories(user_id, limit=100)
        
        # Clear current conversation
        st.session_state.conversation_history = []
        st.session_state.messages = []
        
        # Sort memories by timestamp if available
        if memories:
            memories.sort(key=lambda x: x.get('timestamp', '0'))
            
            # Reconstruct conversation from memories
            for memory in memories:
                message_type = memory.get('message_type', 'user')
                message_content = memory.get('message', '')
                
                if message_content:
                    st.session_state.messages.append({
                        "role": message_type if message_type in ['user', 'assistant'] else 'user',
                        "content": message_content
                    })
                    
                    # Also add to conversation history for context
                    st.session_state.conversation_history.append((message_type, message_content))
        
        st.session_state.user_id = user_id
        st.success(f"Loaded conversation for User ID: {user_id}")
        
    except Exception as e:
        logger.error(f"Error loading user conversation: {str(e)}")
        st.error(f"Error loading conversation: {str(e)}")

def clear_conversation():
    """Clear the current session messages but keep user ID"""
    st.session_state.conversation_history = []
    st.session_state.messages = []
    # Keep the user_id and user_id_input so user can reload conversation
    st.success("Current session cleared! Your conversation history is still saved - reload to see it again.")

async def get_bot_response(user_input: str, user_id: str, conversation_history: List[Tuple[str, str]]) -> str:
    """Get response from the memory-enabled chatbot"""
    try:
        response = await process_query_with_memory(user_id, user_input, conversation_history)
        return response
    except Exception as e:
        logger.error(f"Error getting bot response: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

def retrieve_user_memories(user_id: str, query: str = "", top_k: int = 10) -> List[str]:
    """Retrieve memories for the current user"""
    try:
        if not query:
            query = "general conversation"
        memories = memory_service.retrieve_memories(user_id, query, top_k)
        logger.info(f"Retrieved {len(memories)} memories for query: {query}")
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        return []

def get_all_user_memories(user_id: str) -> List[dict]:
    """Get all memories for debugging"""
    try:
        memories = memory_service.get_all_user_memories(user_id, limit=50)
        return memories
    except Exception as e:
        logger.error(f"Error getting all memories: {str(e)}")
        return []

def test_memory_storage(user_id: str) -> str:
    """Test if memory storage is working"""
    try:
        test_message = f"Test message at {time.time()}"
        memory_service.store_message(user_id, test_message, "test")
        
        # Try to retrieve it
        time.sleep(1)  # Give it a moment
        memories = memory_service.retrieve_memories(user_id, "test message", 5)
        
        if any("test message" in memory.lower() for memory in memories):
            return "✅ Memory storage is working!"
        else:
            return "❌ Memory storage test failed - message not found in retrieval"
            
    except Exception as e:
        return f"❌ Memory storage test failed: {str(e)}"

def main():
    # Initialize session
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🧠 Memory-Enabled AI Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("👤 User Management")
        
        # User ID input
        user_id_input = st.text_input(
            "Enter your User ID:",
            value=st.session_state.user_id_input,
            placeholder="e.g., john_doe_123",
            help="Enter your unique user ID to load your conversation history"
        )
        
        # Load user conversation button
        if st.button("🔄 Load Conversation", use_container_width=True):
            if user_id_input.strip():
                st.session_state.user_id_input = user_id_input.strip()
                load_user_conversation(user_id_input.strip())
                st.rerun()
            else:
                st.error("Please enter a valid User ID")
        
        # Current user info
        if st.session_state.user_id:
            st.info(f"**Current User:** {st.session_state.user_id}")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reload", use_container_width=True, help="Reload conversation history from memory"):
                    load_user_conversation(st.session_state.user_id)
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear", use_container_width=True, help="Clear current session (history preserved)"):
                    clear_conversation()
                    st.rerun()
        else:
            st.warning("Please enter your User ID to start chatting")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display conversation history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    # Chat input
    chat_disabled = st.session_state.processing or not st.session_state.user_id
    chat_placeholder = "Enter your User ID first..." if not st.session_state.user_id else "Type your message here..."
    
    user_input = st.chat_input(chat_placeholder, disabled=chat_disabled)
    
    if user_input and not st.session_state.processing and st.session_state.user_id:
        # Add user message to session
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.processing = True
        
        # Display user message immediately
        st.markdown(
            f'<div class="chat-message user-message"><strong>You:</strong> {user_input}</div>',
            unsafe_allow_html=True
        )
        
        # Show typing indicator
        with st.spinner("Assistant is thinking..."):
            # Get bot response
            try:
                logger.info(f"Processing message for user {st.session_state.user_id[:8]}: {user_input}")
                
                response = asyncio.run(get_bot_response(
                    user_input, 
                    st.session_state.user_id, 
                    st.session_state.conversation_history
                ))
                
                logger.info(f"Got response: {response[:100]}...")
                
                # Add to conversation history
                st.session_state.conversation_history.append(("user", user_input))
                st.session_state.conversation_history.append(("assistant", response))
                
                # Add assistant message to session
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Log memory storage attempt
                logger.info("Messages should now be stored in memory")
                
            except Exception as e:
                logger.error(f"Error in chat processing: {str(e)}", exc_info=True)
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            finally:
                st.session_state.processing = False
        
        # Rerun to update the display
        st.rerun()
    
    # Instructions
    with st.expander("ℹ️ How to use this chatbot"):
        st.markdown("""
        ### Features:
        - **Memory-Enabled Conversations**: The bot remembers your past interactions across sessions
        - **User ID Based**: Your conversations persist based on your unique User ID
        - **Conversation History**: Automatically loads your past conversations when you enter your User ID
        - **Persistent Context**: Your conversations are stored permanently and can be accessed anytime
        
        ### How to Start:
        1. **Enter your User ID** in the sidebar (e.g., "john_doe_123", "alice2024", etc.)
        2. **Click "Load Conversation"** to retrieve your chat history
        3. **Start chatting** - the bot remembers everything from previous sessions
        
        ### Tips:
        - Use a consistent User ID to maintain your conversation history
        - **Clear vs Reload**: "Clear" only clears the current session - your history is preserved in memory
        - **Reload** anytime to restore your full conversation history
        - Ask about past conversations: "What did we discuss about..."
        - Reference previous topics: "Remember when we talked about..."
        - The bot will automatically use relevant memories to provide better responses
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Powered by OpenAI GPT-4 and Pinecone Vector Database</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
