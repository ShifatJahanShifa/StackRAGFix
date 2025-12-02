from pydantic import BaseModel


class BugFixingDTO(BaseModel):
    prompt: str
