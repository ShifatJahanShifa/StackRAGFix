We use baseModel from pydantic. It is used for:
- parsing and validating request data
- automatic documentation generation (swagger API)
- type hints and autocomplete
- data convertion 

Properties of a stack overflow question to be stored:
- question's id
- question's link
- quedtion's title
- question's body
- question's tags
- question's creation date
- is_answered 

tags: target_tags = [
    "python", "javascript", "typescript", "java", "c#", "cpp", "go", "rust",
    "reactjs", "node.js", "express", "next.js", "angular", "vue.js",
    "django", "flask", "spring-boot", "fastapi",
    "mongodb", "mysql", "postgresql",
    "git", "docker", "eslint", "webpack",
    "pytest", "jest", "unittest",
    "debugging", "refactoring", "bug", "exception", "error-handling"
]

target_tags = [
    "python", "javascript", "typescript", "reactjs",
    "node.js", "express", "django", "flask",
    "java", "spring-boot", "mongodb", "postgresql",
    "debugging", "refactoring", "error-handling"
]
