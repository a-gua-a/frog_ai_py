import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.postgres import PostgresStore
from agent.ChatModel import chatModel
from Tools.WebSearchTool import webSearchTool
from common.constant.ChatAgentBaseConstant import baseRoleDescription

checkpointer = InMemorySaver()

DB_BASE_URL = os.getenv("DB_BASE_URL")
if DB_BASE_URL is None:
    raise ValueError("环境变量 DB_BASE_URL 未设置")

summarization = SummarizationMiddleware(
    model=chatModel,
    trigger_on=("tokens", 3000),
    summary_prompt="请总结以上内容。",
    keep_messages=("messages", 10)
)

with PostgresStore.from_conn_string(DB_BASE_URL) as store:
    store.setup()
    LuciaChatAgent = create_agent(
        name="LuciaChatAgent",
        model=chatModel,
        store=store,
        middleware=[summarization],
        checkpointer=checkpointer,
        system_prompt=baseRoleDescription,
        tools=[webSearchTool]
    )
