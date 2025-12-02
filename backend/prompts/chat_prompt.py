CHAT_PROMPT = """
You are the final step of this architecture. Construct the final answer based on the given question and evidence.
Be thorough — if you write code, include every necessary detail. 
Indicate whether the Stack Overflow answer you used was an accepted one.
At the end, mention all links of the answers you used in the format:
Links used:
- [Question Title] Link1
- [Question Title] Link2
- [Question Title] Link3

User Question: {question}
Relevant Stack Overflow Threads: {evidence}
"""
