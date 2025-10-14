from pydantic import BaseModel
from typing import List, Dict, Optional


class SearchRequest(BaseModel):
    query: str
    k: int = 20


class SearchResponse(BaseModel):
    result: str
