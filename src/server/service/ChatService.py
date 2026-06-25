from langchain_core.messages import HumanMessage
from typing import Any
from langchain_core.runnables import RunnableConfig
import common.entity.ChatRequest as ChatRequest
import agent.LuciaChatAgent
import uuid
import logging
logger = logging.getLogger(__name__)

class ChatService:
    async def commonChat(self, request: ChatRequest) -> Any:
        chatAgent = agent.LuciaChatAgent.LuciaChatAgent
        if request.message is None:
            raise Exception("问题不能为空")
        message = request.message
        if request.thread_id is None:
            threadId = str(uuid.uuid4())
        else:
            threadId = request.thread_id
        config: RunnableConfig = {
            "configurable":{
                "thread_id": threadId
            }
        }
        userInput = {
            "messages": [HumanMessage(content=message)]
        }
        async for chunk in chatAgent.astream(
            input=userInput,
            config=config,
            stream_mode="messages"
        ):
            # chunk 是 (message, metadata) 元组
            message_obj, metadata = chunk
            # 只 yield 消息内容（字符串），跳过空内容
            if hasattr(message_obj, "content") and message_obj.content:
                logger.info(message_obj.content)
                yield message_obj.content

chatService = ChatService()