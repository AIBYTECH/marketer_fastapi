from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Marketer Chatbot API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for chat histories (in production, use a database)
chat_histories = {}

# Pydantic models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chat_id: str

class ChatHistoryResponse(BaseModel):
    chat_id: str
    messages: List[ChatMessage]
    created_at: str

# Initialize LLM
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is required")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, max_tokens=500)

def get_llm_response(query: str, chat_history: List[dict]) -> str:
    """Generate LLM response based on query and chat history"""
    template = """
    You are a digital marketing assistant. Provide helpful advice and strategies for the user's digital marketing needs, considering the history of the conversation:
    
    Chat history: {chat_history}
    User question: {user_question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    # Convert chat history to string format
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    
    return chain.invoke({
        "chat_history": history_str,
        "user_question": query
    })

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Generate or use existing chat ID
        chat_id = request.chat_id or str(uuid.uuid4())
        
        # Initialize chat history if new chat
        if chat_id not in chat_histories:
            chat_histories[chat_id] = {
                "messages": [
                    {"role": "assistant", "content": "Hello, I am your digital marketing assistant. How can I assist you today?"}
                ],
                "created_at": datetime.now().isoformat()
            }
        
        # Add user message to history
        chat_histories[chat_id]["messages"].append({
            "role": "user", 
            "content": request.message
        })
        
        # Get LLM response
        response = get_llm_response(request.message, chat_histories[chat_id]["messages"])
        
        # Add assistant response to history
        chat_histories[chat_id]["messages"].append({
            "role": "assistant", 
            "content": response
        })
        
        return ChatResponse(response=response, chat_id=chat_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str):
    """Get chat history by ID"""
    if chat_id not in chat_histories:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat_data = chat_histories[chat_id]
    return ChatHistoryResponse(
        chat_id=chat_id,
        messages=[ChatMessage(**msg) for msg in chat_data["messages"]],
        created_at=chat_data["created_at"]
    )

@app.get("/api/chats")
async def list_chats():
    """List all chat sessions"""
    return {
        "chats": [
            {
                "chat_id": chat_id,
                "created_at": data["created_at"],
                "message_count": len(data["messages"])
            }
            for chat_id, data in chat_histories.items()
        ]
    }

@app.post("/api/chat/new")
async def new_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    chat_histories[chat_id] = {
        "messages": [
            {"role": "assistant", "content": "Hello, I am your digital marketing assistant. How can I assist you today?"}
        ],
        "created_at": datetime.now().isoformat()
    }
    return {"chat_id": chat_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
