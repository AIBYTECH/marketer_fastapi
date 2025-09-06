from fastapi import FastAPI, Request, HTTPException
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




@app.get("/", response_class=HTMLResponse)
async def index():
"""Serve the single-page frontend."""
html_path = os.path.join("templates", "index.html")
if not os.path.exists(html_path):
return HTMLResponse(content="<h1>Index not found</h1>", status_code=404)
return FileResponse(html_path)




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