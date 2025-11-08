import src.config 
# from backend.models.model import Model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from  models.model_instance import chatModel, embeddingModel

question_divider = LLMChain(
    llm=chatModel,
    prompt=PromptTemplate.from_template(src.config.QUESTION_DIVIDER_PROMPT)
)

keyword_extractor = LLMChain(
        llm=chatModel,
        prompt=PromptTemplate.from_template(src.config.KEYWORD_EXTRACTOR_PROMPT)
    )

question_complexity_checker = LLMChain(
    llm=chatModel,
    prompt=PromptTemplate.from_template(src.config.QUESTION_COMPLEXITY_CHECKER_PROMPT)
)

evidence_scorer = LLMChain(
    llm=chatModel,
    prompt=PromptTemplate.from_template(src.config.EVIDENCE_SCORER_PROMPT)
)

evidence_checker = LLMChain(
    llm=chatModel,
    prompt=PromptTemplate.from_template(src.config.EVIDENCE_CHECKER_PROMPT)
)

answer_generator = LLMChain(
    llm=chatModel,
    prompt=PromptTemplate.from_template(src.config.FINAL_ANSWER_GENERATOR_PROMPT)
)