from fastapi import FastAPI

from dtos.generate_request import GenerateRequest
from src.orchestrator import generate_full_response
# from src.full_code import generate_response
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI server 🚀"}

@app.post("/generate")
def generate(request: GenerateRequest):
    prompt = request.prompt
    response = generate_full_response(prompt) 
    # generate_response(prompt)
    # response_text = f"Generated response for: {prompt}"
    print(response)
    return {"prompt": prompt, "response": response}
