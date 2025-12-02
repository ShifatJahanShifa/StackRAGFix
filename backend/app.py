from fastapi import FastAPI

from constants.api import API_VERSION
from dtos.bug_fixing import BugFixingDTO
from dtos.chat import ChatDTO
from dtos.code_refactoring import CodeRefactoringDTO
from src.bug_fixing import fix_bug
from src.chat import generate_chat_response
from src.code_refactoring import refactor_code

app = FastAPI()


@app.get(f"{API_VERSION}/")
def root():
    return {"message": "Welcome to the StackRAG server 🚀"}


@app.post(f"{API_VERSION}/chat")
async def chat_handler(request: ChatDTO):
    prompt = request.prompt
    response = await generate_chat_response(prompt)
    print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"{API_VERSION}/refactoring")
async def code_refactoring_handler(request: CodeRefactoringDTO):
    prompt = request.prompt
    response = await refactor_code(prompt)
    print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"{API_VERSION}/bugfix")
async def bug_fixing_handler(request: BugFixingDTO):
    prompt = request.prompt
    response = await fix_bug(prompt)
    print(response)
    return {"prompt": prompt, "response": response}
