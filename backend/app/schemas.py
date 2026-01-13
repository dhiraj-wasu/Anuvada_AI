from pydantic import BaseModel

class AskRequest(BaseModel):
    problem: str
