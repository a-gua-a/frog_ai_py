from typing import Optional, List, Dict
from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    history: Optional[List[Dict[str, str]]] = None