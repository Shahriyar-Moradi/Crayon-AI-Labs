import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
# from pinecone_service import PineconeService
from graph_state import GraphState

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

def initialize_pinecone_index():
    PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
    INDEX_NAME = "chatbot-memory"
    VECTOR_DIM = 1536
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIM,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Connected to Pinecone index: {INDEX_NAME}")
    
    return pc.Index(INDEX_NAME)

class PineconeService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
        self.index = initialize_pinecone_index()

    def store_message(self, user_id: str, message: str):
        embedding = self.embeddings.embed_query(message)
        self.index.upsert(vectors=[{"id": f"{user_id}-{message}", "values": embedding, "metadata": {"user_id": user_id, "message": message}}])

    def retrieve_memories(self, user_id: str, query: str, top_k: int = 5):
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(vector=query_embedding, top_k=top_k, filter={"user_id": user_id}, include_metadata=True)
        return [match.metadata['message'] for match in results.matches if hasattr(match, 'metadata') and match.metadata]

# Initialize services and models
pinecone_service = PineconeService()
llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini", openai_api_key=os.environ["OPENAI_API_KEY"])

# --- Graph Nodes ---
def store_message_node(state: GraphState):
    """
    Stores the user's message in Pinecone.
    The user's message is the last one in the 'messages' list.
    """
    print("---NODE: STORING MESSAGE---")
    last_message = state["messages"][-1]
    if isinstance(last_message, HumanMessage):
        pinecone_service.store_message(user_id=state["user_id"], message=last_message.content)
    return {}

def retrieve_memories_node(state: GraphState):
    """
    Retrieves memories from Pinecone based on the latest user message.
    """
    print("---NODE: RETRIEVING MEMORIES---")
    last_message = state["messages"][-1]
    memories = pinecone_service.retrieve_memories(user_id=state["user_id"], query=last_message.content)
    return {"retrieved_memories": memories}

def generate_response_node(state: GraphState):
    """
    Generates a response using the LLM, potentially with retrieved memories as context.
    The response is returned as an AIMessage to be added to the state.
    """
    print("---NODE: GENERATING RESPONSE---")
    prompt_template = """You are a helpful chatbot with memory. Your user ID is {user_id}.

Use the following retrieved memories to enhance your response if they are relevant:
<memories>
{memories}
</memories>

Respond to the last user message in the conversation below.

{messages}
"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm

    # The entire message history is now passed to the LLM
    response = chain.invoke({
        "user_id": state["user_id"],
        "memories": "\n".join(state.get("retrieved_memories", [])), # <-- THE FIX
        "messages": state["messages"]
    })
    
    # Return an AIMessage to be appended to the 'messages' list in the state
    return {"messages": [AIMessage(content=response.content)]}


# --- Conditional Router ---

def should_retrieve_router(state: GraphState):
    """
    A router that decides whether to retrieve memories or go straight to generation.
    """
    print("---ROUTER: SHOULD RETRIEVE?---")
    if len(state["messages"]) <= 1: # If it's the first message, no need to retrieve
        print("---DECISION: NO (first message)---")
        return "generate"
    
    last_message = state["messages"][-1]
    prompt = f"""Given the conversation history and the user's latest message, should I retrieve past memories to answer the user's question?
The user's latest message is: '{last_message.content}'

Answer with only 'yes' or 'no'."""
    
    router_llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_API_KEY"])
    response = router_llm.invoke(prompt)
    
    if "yes" in response.content.lower():
        print("---DECISION: YES---")
        return "retrieve"
    else:
        print("---DECISION: NO---")
        return "generate"