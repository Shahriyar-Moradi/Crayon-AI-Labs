# 🧠 Memory-Enabled AI Chatbot - Streamlit App

A beautiful web interface for your memory-enabled AI chatbot powered by OpenAI GPT-4 and Pinecone vector database.

## ✨ Features

- **🧠 Memory-Enabled Conversations**: The bot remembers your past interactions across sessions
- **💬 Real-time Chat Interface**: Beautiful, responsive chat UI with message history
- **🔧 Session Management**: Start new sessions or clear current conversations
- **🔍 Memory Search**: Search through your conversation history with semantic search
- **📊 Statistics**: View conversation metrics and memory analytics
- **🎨 Modern UI**: Clean, professional interface with custom styling

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file in the OpenAI_Agent directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
MEMORY_INDEX_NAME=chatbot-memory
MODEL_CHOICE=gpt-4o-mini
```

### 3. Run the App

Option A - Using the run script:
```bash
python run_streamlit.py
```

Option B - Direct Streamlit command:
```bash
streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 🎯 How to Use

### Basic Chat
1. Type your message in the chat input at the bottom
2. Press Enter or click the send button
3. The AI will respond using its memory of past conversations

### Session Management
- **New Session**: Start fresh with a new user ID (sidebar)
- **Clear Chat**: Clear current conversation but keep the same user ID
- **Session ID**: Each session has a unique identifier for memory storage

### Memory Features
- **Automatic Memory**: All conversations are automatically stored
- **Memory Search**: Use the sidebar to search through past conversations
- **Context Awareness**: The bot references relevant past conversations automatically

### Memory Search
1. Enter keywords in the "Search memories" field in the sidebar
2. Adjust the number of memories to retrieve (1-20)
3. Click "🔍 Retrieve Memories" to see relevant past conversations

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Backend**: OpenAI GPT-4 via the `agents` library
- **Memory**: Pinecone vector database for semantic memory storage
- **Embeddings**: OpenAI text-embedding-3-small for vectorization

### Key Components
- `streamlit_app.py`: Main Streamlit application
- `my_agent2.py`: Memory-enabled chatbot agent
- `run_streamlit.py`: Convenience script to run the app

### Memory System
- Each user gets a unique session ID
- Messages are automatically stored as embeddings in Pinecone
- Relevant memories are retrieved using semantic similarity
- Conversation context is maintained across sessions

## 🎨 UI Features

### Chat Interface
- **User Messages**: Blue-themed bubbles on the right
- **Assistant Messages**: Purple-themed bubbles on the left
- **Real-time Updates**: Messages appear instantly as they're typed
- **Scrollable History**: Full conversation history with smooth scrolling

### Sidebar Features
- **Session Controls**: New session and clear chat buttons
- **Memory Management**: Search and retrieve past conversations
- **Statistics**: Live metrics about your conversation

### Responsive Design
- Works on desktop and mobile devices
- Collapsible sidebar for mobile viewing
- Adaptive layout based on screen size

## 🔧 Configuration

### Environment Variables
```env
OPENAI_API_KEY=sk-...                 # Your OpenAI API key
PINECONE_API_KEY=...                  # Your Pinecone API key
MEMORY_INDEX_NAME=chatbot-memory      # Name for your Pinecone index
MODEL_CHOICE=gpt-4o-mini             # OpenAI model to use
```

### Streamlit Configuration
The app runs with these default settings:
- **Port**: 8501
- **Host**: localhost
- **Usage Stats**: Disabled for privacy

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure your `.env` file contains valid API keys
   - Check that the `.env` file is in the correct directory

2. **Pinecone Connection Issues**
   - Verify your Pinecone API key is correct
   - Check your Pinecone index configuration

3. **Import Errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Ensure you're using Python 3.8 or higher

4. **Streamlit Won't Start**
   - Check if port 8501 is already in use
   - Try running with `--server.port 8502` for a different port

### Error Messages

If you see "ServerlessSpec not found" warnings:
- This is normal for some Pinecone versions
- The app will automatically fall back to compatible methods

## 📝 Example Conversations

Try these conversation starters to test the memory features:

1. **Initial conversation**: "Hi, my name is John and I love pizza"
2. **Later session**: "What do you remember about my food preferences?"
3. **Memory search**: Search for "pizza" in the sidebar to find past mentions

## 🔐 Privacy & Security

- All conversations are stored in your personal Pinecone index
- Session IDs are randomly generated UUIDs
- No data is shared with third parties beyond OpenAI and Pinecone APIs
- You can clear your conversation history at any time

## 📋 Requirements

- Python 3.8+
- OpenAI API account
- Pinecone account
- All dependencies listed in `requirements.txt`

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is part of the broader AI agent system. See the main README for license information. 