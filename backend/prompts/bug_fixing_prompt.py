BUG_FIXING_PROMPT = """
You are the final step of this architecture. Construct the final answer based on the given question and evidence.
Be thorough — if you fix the code, include every necessary detail. 
Tell the reason for the bug and how your solution will fix the bug. 
Indicate whether the Stack Overflow answer you used was an accepted one.
At the end, mention all links of the answers you used in the format:
Links used:
- [Question Title] Link1
- [Question Title] Link2
- [Question Title] Link3
If there is no relevant Stack Overflow Threads to fix the bug, try to fix the bug on your own.

User Question: {question}
Relevant Stack Overflow Threads: {evidence}
"""
