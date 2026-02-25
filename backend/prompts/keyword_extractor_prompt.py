KEYWORD_EXTRACTOR_PROMPT = """
You are given a technical question. You have to use the question to create a Python list of short search queries that will be useful for searching on Stack Overflow.
Make every query in the list as short as possible (less than 4 words), but make sure you do not omit important search terms or make it too general.
Each query must be a short phrase enclosed in double quotes. 
Question: {question}
"""
