from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str
    type: str  # 'hook' or 'rewrite'
    platform: Optional[str] = None
    tone: Optional[str] = None

class GenerateResponse(BaseModel):
    content: str

class HistoryItem(BaseModel):
    id: str
    prompt: str
    content: str
    type: str
    platform: Optional[str] = None
    tone: Optional[str] = None
    timestamp: Optional[str] = None

class HistoryResponse(BaseModel):
    history: list[HistoryItem]
