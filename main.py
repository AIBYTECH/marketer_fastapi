from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import LLM-related libraries (same as your streamlit app)
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from fastapi.templating import Jinja2Templates

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    # Allow the app to start — but chat will fail unless API_KEY provided
    print("Warning: API_KEY not set. Set it in environment or .env file.")

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow simple CORS for front-end on same origin / Railway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    # Optional: list of messages as dicts with role/content
    history: list | None = None


def build_prompt(user_question: str, chat_history: list | None):
    template = """
    You are a digital marketing assistant. Provide helpful advice and strategies for the user's digital marketing needs, considering the history of the conversation:
    
    Chat history: {chat_history}
    
    User question: {user_question}
    """
    return ChatPromptTemplate.from_template(template).format({
        "chat_history": chat_history or "",
        "user_question": user_question,
    })


def get_llm_response_sync(query: str, chat_history: list | None):
    """Call the LLM (synchronously) and return a string response.
    This mirrors your Streamlit code but returns full text.
    """
    if not API_KEY:
        raise RuntimeError("API_KEY is not configured on the server.")

    # Create prompt template
    template = """
    You are a digital marketing assistant. Provide helpful advice and strategies for the user's digital marketing needs, considering the history of the conversation:
    
    Chat history: {chat_history}
    
    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=API_KEY, max_tokens=500)
    chain = prompt | llm | StrOutputParser()

    # The Streamlit version used chain.stream (generator). Here we call it as a full run.
    try:
        result = chain({
            "chat_history": chat_history or [],
            "user_question": query
        })
    except Exception as e:
        raise

    # If the result is a generator/iterator, join it
    if hasattr(result, "__iter__") and not isinstance(result, (str, bytes)):
        return "".join(list(result))
    return str(result)



templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Receive a chat message + optional history, return assistant reply.

    Request JSON: { message: str, history: [{role, content}, ...] }
    Response JSON: { reply: str }
    """
    try:
        reply = get_llm_response_sync(req.message, req.history)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Log or return generic message
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return JSONResponse({"reply": reply})