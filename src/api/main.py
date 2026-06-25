import asyncio
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()             # 输出到控制台
    ]
)
from api.ChatAPI import app

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    asyncio.run(server.serve(), loop_factory=asyncio.SelectorEventLoop)
