from fastapi import FastAPI
from pydantic import BaseModel
from services.chat import agent


app = FastAPI()


@app.get("/")
def read_root():
    return "This is Nmobile chatbot API"


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    token: str
@app.post("/chat")
def chat(request: ChatRequest):
    response = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config={"configurable": {"thread_id": request.session_id, "user_token": request.token}}
        )
    final_message = response["messages"][-1].content
    return {"Response": final_message}

# Run the application using the command:
# uvicorn main:app --reload 
# This will start the server and you can access the endpoints at:
# http://localhost:8000/ for the root endpoint
# http://localhost:8000/items/{item_id} for the items endpoint

