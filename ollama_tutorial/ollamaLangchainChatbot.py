# chatbot with langchain ollama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# construct the template
promptTemplate = """
    Answer the question below. 

    Here is the conversation history for context: {context}

    Question: {question}

    Answer:
"""

llm = ChatOllama(model='llama3:8b')
prompt = ChatPromptTemplate.from_template(promptTemplate)

chain = prompt | llm

def handleChat(): 
    context = ""
    print("Welcome to the AI chatbot! Type 'exit' to quit.")
    while True:
        userInput = input("Human: ") 
        if userInput.lower() == 'exit': 
            break
        response = chain.invoke({"context": context, "question": userInput})
        print("AI: ",response.content)
        context += f"\nUser: {userInput}\nAI: {response.content}"


if __name__ == "__main__":
    handleChat()