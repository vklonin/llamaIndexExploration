import configparser
import json
import os
from datetime import datetime

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

from docs_query_engine import DocsQueryEngine
from git_wraper import get_pull_request_diff

# llm = OpenAI(openai_api_key=os.getenv("OPEN_API_KEY"))
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
# llm_creative = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")

template_review_prompt = """You are a senior developer working on a new a project 
Make a following pull request overview:

{pull_request}

Review Criteria:
Please focus your review on the following aspects:

Code Quality: Assess the overall code quality, readability, and maintainability of the changes. Are coding conventions followed? Is the code well-documented?

Functionality: Verify that the proposed changes work as intended and do not introduce new bugs or regressions.

Feedback:
Provide constructive feedback for the pull request author. If you have identified any issues or concerns, please be specific and suggest potential improvements or alternative approaches.

"""

review_generation_prompt = PromptTemplate(
    input_variables=["pull_request"],
    template=template_review_prompt
)

pr = get_pull_request_diff("jdi-testing","jdi-light",5023,os.getenv("GITHUB_TOKEN"))

raw_prompt = review_generation_prompt.format_prompt(pull_request=pr).to_string()


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('configPR.txt')

    owner = config.get('variables', 'owner')
    repo = config.get('variables', 'repo')
    file = config.get('variables', 'file')
    filter_dirs = json.loads(config.get('variables', 'filter_dirs'))
    branch = config.get('variables', 'branch')

    query_engine = DocsQueryEngine(owner, repo, file, filter_dirs, branch)
    result = query_engine.make_qarequest_to_repo(raw_prompt)



    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{current_datetime}-{repo}-review.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)
