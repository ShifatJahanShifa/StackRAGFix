CODE_REFACTORING_PROMPT = """
You are the final step of this architecture. Construct the final answer based on the given question and evidence.
Be thorough — if you refactor code, include every necessary detail showing where you refactored the code. 
Indicate whether the Stack Overflow answer you used was an accepted one.
At the end, mention all links of the answers you used in the format:
Links used:
- [Question Title] Link1
- [Question Title] Link2
- [Question Title] Link3
If there is no relevant Stack Overflow Threads to refactor the code, try to refactor the code on your own.

User Question: {question}
Relevant Stack Overflow Threads: {evidence}
"""
