from fastapi import FastAPI

from backend.dtos.code_refactoring import CodeRefactoringDTO
from constants.api import API_VERSION
from dtos.bug_fixing import BugFixingDTO
from dtos.chat import ChatDTO
from src.bug_fixing import fix_bug
from src.chat import generate_chat_response
from src.code_refactoring import refactor_code

app = FastAPI()


@app.get(f"{API_VERSION}/")
def root():
    return {"message": "Welcome to the FastAPI server 🚀"}


@app.post(f"{API_VERSION}/chat")
def generate(request: ChatDTO):
    prompt = request.prompt
    response = generate_chat_response(prompt)
    print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"{API_VERSION}/refactoring")
def generate(request: CodeRefactoringDTO):
    prompt = request.prompt
    response = refactor_code(prompt)
    print(response)
    return {"prompt": prompt, "response": response}


@app.post(f"{API_VERSION}/bugfix")
def generate(request: BugFixingDTO):
    prompt = request.prompt
    response = fix_bug(prompt)
    print(response)
    return {"prompt": prompt, "response": response}
