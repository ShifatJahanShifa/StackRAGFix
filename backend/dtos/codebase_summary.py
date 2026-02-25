from pydantic import BaseModel


class CodebaseSummaryDTO(BaseModel):
    prompt: str
    codebase: str
