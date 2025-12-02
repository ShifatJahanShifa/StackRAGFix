from pydantic import BaseModel


class CodeRefactoringDTO(BaseModel):
    prompt: str
