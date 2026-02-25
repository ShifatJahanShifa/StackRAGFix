from pydantic import BaseModel


class ChatDTO(BaseModel):
    prompt: str
    language: str
    history: list[dict[str, str]]
    currentFileName: str
    currentFileContent: str
    selectedFilesContent: str
    code: str
