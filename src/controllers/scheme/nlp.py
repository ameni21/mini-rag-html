from pydantic import BaseModel
from typing import  Optional

class PushRequest(BaseModel): 
    do_rest: Optional[int] = 0


class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5

class GraphRequest(BaseModel):
    text: str