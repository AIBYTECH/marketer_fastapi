from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# --------------------
# Load Environment
# --------------------
load_dotenv()
api_key = os.getenv("API_KEY")

app = FastAPI(title="Digital Marketing Assistant API")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your Railway domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Schemas
# --------------------
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    chat_history: List[Message]

class ChatResponse(BaseModel):
    response: str

# --------------------
# LLM Response
# --------------------
def get_llm_response(query: str, chat_history: List[Message]) -> str:
    template = """
    You are a digital marketing assistant. Provide helpful advice and strategies for the user's digital marketing needs, considering the history of the conversation:
    
    Chat history: {chat_history}
    
    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        max_tokens=500
    )
    chain = prompt | llm | StrOutputParser()

    formatted_history = []
    for msg in chat_history:
        if msg.role.lower() == "human":
            formatted_history.append(HumanMessage(content=msg.content))
        else:
            formatted_history.append(AIMessage(content=msg.content))

    response_gen = chain.stream({
        "chat_history": formatted_history,
        "user_question": query
    })
    return ''.join(list(response_gen))

# --------------------
# API Routes
# --------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = get_llm_response(request.query, request.chat_history)
    return ChatResponse(response=response)

# --------------------
# Serve Frontend
# --------------------
# Serve static files (optional: css/js/images)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return FileResponse("index.html")
