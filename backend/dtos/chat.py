from pydantic import BaseModel


class ChatDTO(BaseModel):
    prompt: str
