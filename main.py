from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import LLM-related libraries - using Groq directly instead of LangChain
import requests
import json

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
    """Call the Groq API directly and return a string response."""
    if not API_KEY:
        raise RuntimeError("API_KEY is not configured on the server.")

    # Prepare the chat history for the API
    messages = []
    
    # Add chat history if provided
    if chat_history:
        for msg in chat_history:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": content})
    
    # Add the current user query
    messages.append({"role": "user", "content": query})
    
    # Add system message
    system_message = "You are a digital marketing assistant. Provide helpful advice and strategies for the user's digital marketing needs."
    messages.insert(0, {"role": "system", "content": system_message})

    # Call Groq API
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected API response format: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")



@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(static_path)


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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, port=port)