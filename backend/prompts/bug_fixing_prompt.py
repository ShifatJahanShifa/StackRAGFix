# BUG_FIXING_PROMPT = """
# You are the final step of this architecture. Construct the final answer based on the given question and evidence.
# Be thorough — if you fix the code, include every necessary detail.
# Tell the reason for the bug and how your solution will fix the bug.
# Indicate whether the Stack Overflow answer you used was an accepted one.
# At the end, mention all links of the answers you used in the format:
# Links used:
# - [Question Title] Link1
# - [Question Title] Link2
# - [Question Title] Link3
# If there is no relevant Stack Overflow Threads to fix the bug, try to fix the bug on your own.

# User Question: {question}
# Relevant Stack Overflow Threads: {evidence}
# """

BUG_FIXING_PROMPT = """
You are the final step of this architecture. Construct the final answer based on the given question, evidence from stack overflow, previous conversation history, 
relevant code retrieved from the codebase, currently active file name, currently active file content and selected files content.
Be thorough — if you fix the code, include every necessary detail. 
Tell the reason for the bug and how your solution will fix the bug. 
Indicate whether the Stack Overflow answer you used was an accepted one.
At the end, mention all links of the answers you used in the format:
Links used:
- [Question Title] Link1
- [Question Title] Link2
- [Question Title] Link3
If there is no relevant Stack Overflow Threads to fix the bug, try to fix the bug on your own.
Also mention that whether you used the relevant code from the codebase or not, from the file content or not and if you used, mention the file name and the code.

User Question: {question}
Relevant Stack Overflow Threads: {evidence}
Previous Conversation History: {history}
Relevant Code Retrieved from the Codebase: {code}
Currently Active File Name: {currentFileName}
Currently Active File Content: {currentFileContent}
Selected Files Content: {selectedFilesContent}
"""
