from pydantic import BaseModel
from typing import List, Dict, Optional

class GapRequest(BaseModel):
    user_id: str
    target_roles: List[str]
    state: str
