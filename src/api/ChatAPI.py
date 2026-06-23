from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from server.service import chatService

app = FastAPI(title="LuciaChatAgent API", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    history: Optional[List[Dict[str, str]]] = None

class TTSRequest(BaseModel):
    text: str

@app.post("/chat/common")
async def commonChat(request: ChatRequest):
    async def generate():
        async for chunk in chatService.commonChat(request):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/event-stream")
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)