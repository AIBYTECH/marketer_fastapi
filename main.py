from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Union
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# ----------------------
# Load Environment Variables
# ----------------------
load_dotenv()
api_key = os.getenv("API_KEY")

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="Digital Marketing Assistant API")

# ----------------------
# Request Schema
# ----------------------
class Message(BaseModel):
    role: str  # "human" or "ai"
    content: str

class ChatRequest(BaseModel):
    query: str
    chat_history: List[Message]

class ChatResponse(BaseModel):
    response: str


# ----------------------
# LLM Response Function
# ----------------------
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

    # Convert Pydantic Message into LangChain Message objects
    formatted_history = []
    for msg in chat_history:
        if msg.role.lower() == "human":
            formatted_history.append(HumanMessage(content=msg.content))
        else:
            formatted_history.append(AIMessage(content=msg.content))

    # Run the chain
    response_gen = chain.stream({
        "chat_history": formatted_history,
        "user_question": query
    })
    response = ''.join(list(response_gen))
    return response


# ----------------------
# API Endpoint
# ----------------------
@app.post("/cha", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = get_llm_response(request.query, request.chat_history)
    return ChatResponse(response=response)


# ----------------------
# Root Endpoint
# ----------------------
@app.get("/")
async def root():
    return {"message": "Digital Marketing Assistant API is running"}
