from pydantic import BaseModel

class SchemeSchema(BaseModel):
    id: str
    title: str
