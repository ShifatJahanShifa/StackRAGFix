from pydantic import BaseModel


class BugFixingDTO(BaseModel):
    prompt: str
    language: str
    history: list[dict[str, str]]
    currentFileName: str
    currentFileContent: str
    selectedFilesContent: str
    code: str
