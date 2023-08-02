import configparser
import json
from datetime import datetime

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

from docs_query_engine import DocsQueryEngine

# llm = OpenAI(openai_api_key=os.getenv("OPEN_API_KEY"))
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
# llm_creative = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")

template_generation_prompt_tm = """You are a developer working on a new project {description} and need a well-structured README.md 
file to help others understand and use your project. Write a detailed and informative README.md template. Make sure 
the prompt includes sections like project overview, installation instructions, usage examples, contributing 
guidelines, and licensing information.

result must be only an README.MD template
"""

template_generation_prompt = PromptTemplate(
    input_variables=["description"],
    template=template_generation_prompt_tm
)

md_template = LLMChain(llm=llm, prompt=template_generation_prompt).run(description="")

result_prompt_template = """
You are a developer working on a new project and need a well-structured README.md 
file to help others understand and use your project. 
Write a detailed and informative README.md based on a template provided here:
{md_template}
Use a full description of all project classes provided here:
{classes_description}
Use all endpoints description for this project provided here:
{endpoints_description}

result must be only an README.MD 
"""

summary_prompt_template = PromptTemplate(
    input_variables=["md_template", "classes_description", "endpoints_description"],
    template=result_prompt_template
)


if __name__ == "__main__":

    # owner = "jdi-testing"
    # repo = "jdi-light"
    # file = "java"
    # filter_dirs = ["jdi-bdd",
    #                 "jdi-bdd-tests",
    #                 "jdi-eyes-demo",
    #                 "jdi-light-angular",
    #                 "jdi-light-angular-tests",
    #                 "jdi-light-angular-tests-with-mocks",
    #                 "jdi-light-applitools-tests",
    #                 "jdi-light-bootstrap",
    #                 "jdi-light-bootstrap-tests",
    #                 "jdi-light-eyes",
    #                 "jdi-light-html",
    #                 "jdi-light-html-selenium3",
    #                 "jdi-light-html-tests",
    #                 "jdi-light-material-ui",
    #                 "jdi-light-material-ui-tests",
    #                 "jdi-light-mobile",
    #                 "jdi-light-mobile-bootstrap-web-tests",
    #                 "jdi-light-mobile-html-web-tests",
    #                 "jdi-light-mobile-selenium3",
    #                 "jdi-light-mobile-selenium3-tests",
    #                 "jdi-light-mobile-tests",
    #                 "jdi-light-selenium3",
    #                 "jdi-light-vuetify",
    #                 "jdi-light-vuetify-tests",
    #                 "test-examples",
    #                 "test-templates",
    #                ]

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('config2.txt')

    owner = config.get('variables', 'owner')
    repo = config.get('variables', 'repo')
    file = config.get('variables', 'file')
    filter_dirs = json.loads(config.get('variables', 'filter_dirs'))
    branch = config.get('variables', 'branch')

    query_engine = DocsQueryEngine(owner, repo, file, filter_dirs, branch)
    classes_description = query_engine.explain_each_class()
    endpoints_description = query_engine.explain_each_endpoint()

    summary_chain = LLMChain(llm=llm, prompt=summary_prompt_template)
    result = summary_chain.run(
        md_template=md_template,
        classes_description=classes_description,
        endpoints_description=endpoints_description
    )

    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{current_datetime}-{repo}-readme.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)
