import streamlit as st
import asyncio
import uuid
from typing import List, Tuple
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from git my_agent import process_query_with_memory, memory_service
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
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def clear_conversation():
    """Clear the current conversation"""
    st.session_state.conversation_history = []
    st.session_state.messages = []
    st.success("Conversation cleared!")

def new_session():
    """Start a new session with a new user ID"""
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.conversation_history = []
    st.session_state.messages = []
    st.success(f"New session started! Session ID: {st.session_state.user_id[:8]}...")

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
        st.header("🔧 Session Management")
        
        # Session info
        st.info(f"**Session ID:** {st.session_state.user_id[:8]}...")
        
        # Session controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Session", use_container_width=True):
                new_session()
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_conversation()
                st.rerun()
        
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
    user_input = st.chat_input("Type your message here...", disabled=st.session_state.processing)
    
    if user_input and not st.session_state.processing:
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
        - **Memory-Enabled Conversations**: The bot remembers your past interactions
        - **Session Management**: Start new sessions or clear current conversation
        - **Memory Search**: Search through your conversation history
        - **Persistent Context**: Your conversations are stored and can be referenced later
        
        ### Tips:
        - Ask about past conversations: "What did we discuss about..."
        - Reference previous topics: "Remember when we talked about..."
        - The bot will automatically use relevant memories to provide better responses
        - Use the sidebar to manage your session and explore your conversation history
        """)
    
    # Troubleshooting section
    with st.expander("🔧 Troubleshooting Memory Issues"):
        st.markdown("""
        ### If memories aren't working:
        
        1. **Test the Memory System**: Use the "🧪 Test Memory System" button in the sidebar
        
        2. **Check Memory Statistics**: Look at the statistics in the sidebar - you should see stored memories
        
        3. **View All Memories**: Click "📋 All Memories" to see what's actually stored
        
        4. **Check API Keys**: Ensure your `.env` file has valid OpenAI and Pinecone API keys
        
        5. **Debug Outside Streamlit**: Run `python run_streamlit.py debug` in your terminal
        
        ### Common Issues:
        - **No memories showing**: Check if API keys are correct and Pinecone index exists
        - **Low similarity scores**: Try broader search terms or lower similarity thresholds
        - **Slow responses**: Memory retrieval can take a few seconds for large datasets
        
        ### Memory Search Tips:
        - Use specific keywords from your conversations
        - Try different search terms if nothing appears
        - The system uses semantic similarity, so related concepts should match
        """)
        
        # Add real-time debug info
        if st.button("🔍 Show Debug Info"):
            st.json({
                "user_id": st.session_state.user_id,
                "messages_in_session": len(st.session_state.messages),
                "conversation_history_length": len(st.session_state.conversation_history),
                "processing_status": st.session_state.processing
            })
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Powered by OpenAI GPT-4 and Pinecone Vector Database</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 