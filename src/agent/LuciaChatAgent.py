import os
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph.state import CompiledStateGraph
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.store.postgres import PostgresStore
from psycopg.rows import dict_row

from agent.ChatModel import chatModel
from Tools.WebSearchTool import webSearchTool
from common.constant.ChatAgentBaseConstant import baseRoleDescription
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

DB_BASE_URL = os.getenv("DB_BASE_URL")
if DB_BASE_URL is None:
    raise ValueError("环境变量 DB_BASE_URL 未设置")

summarization = SummarizationMiddleware(
    model=chatModel,
    trigger_on=("tokens", 3000),
    summary_prompt="请总结以上内容。",
    keep_messages=("messages", 10)
)

async def initCheckpointer():
    if DB_BASE_URL is None:
        raise ValueError("环境变量 DB_BASE_URL 未设置")
    conn = await psycopg.AsyncConnection.connect(
        DB_BASE_URL,
        autocommit=True,
        row_factory=dict_row )
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()
    return checkpointer

LuciaChatAgent = None

async def initLuciaChatAgent():
    global LuciaChatAgent
    if DB_BASE_URL is None:
        raise ValueError("环境变量 DB_BASE_URL 未设置")
    checkpointer = await initCheckpointer()
    conn = psycopg.connect(DB_BASE_URL)
    conn.autocommit = True
    store = PostgresStore(conn)
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

