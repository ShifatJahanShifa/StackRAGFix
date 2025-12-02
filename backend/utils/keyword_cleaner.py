import json
import re
from typing import List


def clean_keyword(extracted_keyword_list: List) -> List:
    # for extracted_keyword in extracted_keyword_list:
    #     match = re.search(r"\[([\s\S]*?)\]", extracted_keyword)
    #     if match:
    #         list_str = "[" + match.group(1) + "]"
    #         try:
    #             keywords = ast.literal_eval(list_str)
    #             cleaned_keywords.extend(keywords)
    #         except Exception as e:
    #             print("Error parsing:", e, "\nText:", list_str)

    cleaned_keywords = []
    for extracted_keyword in extracted_keyword_list:
        match = re.search(r"\[([\s\S]*?)\]", extracted_keyword)
        if match:
            list_content = match.group(1)
            keywords = re.findall(r'"([^"]+)"', list_content)
            keywords = [k.strip() for k in keywords if k.strip()]
            cleaned_keywords.extend(keywords)
    return cleaned_keywords


def separate_keyword(extracted_keyword_list: List) -> List:
    safe_keywords = []

    for keyword in extracted_keyword_list:
        try:
            parsed = json.loads(keyword)
            if isinstance(parsed, list):
                safe_keywords.extend(parsed)  # Flatten if it's a list
            else:
                safe_keywords.append(parsed)  # Single value
        except json.JSONDecodeError:
            # If it's not JSON, just append the original string
            safe_keywords.append(keyword)
    return safe_keywords
