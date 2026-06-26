import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List, Dict
from agent.LuciaChatAgent import initLuciaChatAgent
from server.service import chatService
from server.service.TTSService import ttsService
from server.service.FileService import fileService
import asyncio
import logging
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    history: Optional[List[Dict[str, str]]] = None

class TTSRequest(BaseModel):
    text: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initLuciaChatAgent()
    yield

app = FastAPI(title="LuciaChatAgent API", version="1.0.0", lifespan=lifespan)

@app.post("/chat/common")
async def commonChat(request: ChatRequest):
    async def generate():
        async for chunk in chatService.commonChat(request):
            yield chunk
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.websocket("/chat/audio")
async def audioChat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket连接成功")
    request = await websocket.receive_text()
    # 创建队列用于流广播，解决多重消耗问题
    textQueue = asyncio.Queue(maxsize=10)
    ttsQueue = asyncio.Queue(maxsize=10)

    async def stream_broadcaster():
        """将原始文本流写入队列，供多个消费者读取"""
        try:
            async for chunk in chatService.commonChat(request):
                await textQueue.put(chunk)
                await ttsQueue.put(chunk)
        except Exception as e:
            logger.error(f"未知异常: {e}")
        finally:
            await textQueue.put(None)
            await ttsQueue.put(None)  # 结束标记

    # 创建广播任务
    broadcaster = asyncio.create_task(stream_broadcaster())

    # 为TTS服务创建独立的队列读取器
    async def textStream():
        while True:
            chunk = await ttsQueue.get()
            if chunk is None:
                break
            yield chunk
            ttsQueue.task_done()

    audioStream = ttsService.getAudioStream(
        voiceId=os.environ.getenv("VOICEID"),
        textStream=textStream()
    )
    lock = asyncio.Lock()
    async def sendAudio():
        async for chunk in audioStream:
            async with lock:
                logger.info(f"发送音频: {chunk}")
                await websocket.send_bytes(chunk)

    async def sendTest():
        while True:
            chunk = await textQueue.get()
            if chunk is None:
                break
            async with lock:
                logger.info(f"发送文本: {chunk}")
                await websocket.send_text(chunk)
            textQueue.task_done()

    try:
        await asyncio.gather(sendAudio(), sendTest())
    except WebSocketDisconnect:
        logger.error("WebSocket连接异常断开")
    except Exception as e:
        logger.error(f"未知异常: {e}")
    finally:
        broadcaster.cancel()
        await websocket.close()
        logger.info("通讯结束，WebSocket连接正常关闭")

@app.post("/newVoice")
async def newVoice():
    await ttsService.newVoice()

@app.post("/uploadVoiceFile")
async def uploadVoiceFile():
    return fileService.uploadVoiceFile("LuciaVoice.mp3")
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)