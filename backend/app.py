from fastapi import FastAPI

from constants.api import API_VERSION
from dtos.bug_fixing import BugFixingDTO
from dtos.chat import ChatDTO
from dtos.code_refactoring import CodeRefactoringDTO
from dtos.codebase_summary import CodebaseSummaryDTO
from src.bug_fixing import fix_bug
from src.chat import generate_chat_response
from src.code_refactoring import refactor_code
from src.codebase_summary import generate_codebase_summary

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to the StackRAG server"}


@app.get(f"/{API_VERSION}/")
def root():
    return {"message": "Welcome to the StackRAG server"}


@app.post(f"/{API_VERSION}/chat")
async def chat_handler(request: ChatDTO):
    # print("DEBUG: ", request)
    prompt = request.prompt
    language = request.language
    response = await generate_chat_response(prompt, language)
    # print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"/{API_VERSION}/refactoring")
async def code_refactoring_handler(request: CodeRefactoringDTO):
    prompt = request.prompt
    language = request.language
    history = request.history
    code = request.code
    currentFileName = request.currentFileName
    currentFileContent = request.currentFileContent
    selectedFilesContent = request.selectedFilesContent

    response = await refactor_code(
        prompt,
        language,
        history,
        code,
        currentFileName,
        currentFileContent,
        selectedFilesContent,
    )
    # print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"/{API_VERSION}/bugfix")
async def bug_fixing_handler(request: BugFixingDTO):
    prompt = request.prompt
    language = request.language
    history = request.history
    code = request.code
    currentFileName = request.currentFileName
    currentFileContent = request.currentFileContent
    selectedFilesContent = request.selectedFilesContent
    response = await fix_bug(
        prompt,
        language,
        history,
        code,
        currentFileName,
        currentFileContent,
        selectedFilesContent,
    )
    # print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"/{API_VERSION}/codebase-summary")
async def codebase_summary_handler(request: CodebaseSummaryDTO):
    prompt = request.prompt
    codebase = request.codebase
    response = await generate_codebase_summary(codebase)
    # print(response)
    return {"response": response}
