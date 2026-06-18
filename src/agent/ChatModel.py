import os

from langchain.chat_models import init_chat_model

chatModel = init_chat_model(
    model = os.getenv("LLM"),
    model_provider="openai",
    base_url=os.getenv("LLM_API_BASE"),
    api_key = os.getenv("LLM_API_KEY")
)