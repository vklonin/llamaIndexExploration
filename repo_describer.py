import pickle
import os


from llama_index import download_loader, GPTVectorStoreIndex
download_loader("GithubRepositoryReader")

from llama_hub.github_repo import GithubClient, GithubRepositoryReader



owner = "Scorpibear"
repo = "chegura"
file = "js"

# owner = "jdi-testing"
# repo = "jdi-light"
# file = "java"
branch = "master"

docs = None
if os.path.exists("docs.pkl"):
    with open("docs.pkl", "rb") as f:
        docs = pickle.load(f)

if docs is None:
    github_client = GithubClient(os.getenv("GITHUB_TOKEN"))
    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo,
        # filter_directories =     (["jdi-light", "jdi-light-material-ui","jdi-light-material-ui-tests"], GithubRepositoryReader.FilterType.INCLUDE),
        filter_file_extensions=([f".{file}"], GithubRepositoryReader.FilterType.INCLUDE),
        verbose=True,
        concurrent_requests=10,
    )

    docs = loader.load_data(branch=branch)

    with open("docs.pkl", "wb") as f:
        pickle.dump(docs, f)

index = GPTVectorStoreIndex.from_documents(docs)

query_engine = index.as_query_engine()
response = query_engine.query(f"Explain each {repo} class?")
print(response)

response = query_engine.query(f"Stipulate all endpoints with example input and output?")
print(response)

response = query_engine.query(f"Generate README.MD for this project?")
print(response)