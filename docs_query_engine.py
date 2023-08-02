import os
import pickle

from llama_index import download_loader, GPTVectorStoreIndex

download_loader("GithubRepositoryReader")

from llama_hub.github_repo import GithubClient, GithubRepositoryReader


class DocsQueryEngine:
    def __init__(self, owner, repo, file, directories, branch="master", ):
        self.owner = owner
        self.repo = repo
        self.file = file
        self.branch = branch
        self.docs = None
        self.directories = directories

    def load_data(self):
        if os.path.exists("docs.pkl"):
            with open("docs.pkl", "rb") as f:
                self.docs = pickle.load(f)

        if self.docs is None:
            github_client = GithubClient(os.getenv("GITHUB_TOKEN"))
            filter_directories = (
                self.directories, GithubRepositoryReader.FilterType.EXCLUDE) if self.directories else None
            loader = GithubRepositoryReader(
                github_client,
                owner=self.owner,
                repo=self.repo,
                filter_file_extensions=([f".{self.file}"], GithubRepositoryReader.FilterType.INCLUDE),
                filter_directories=filter_directories,
                verbose=True,
                concurrent_requests=10,
            )

            self.docs = loader.load_data(branch=self.branch)

            with open("docs.pkl", "wb") as f:
                pickle.dump(self.docs, f)

    def explain_each_class(self):
        if self.docs is None:
            self.load_data()

        index = GPTVectorStoreIndex.from_documents(self.docs)
        query_engine = index.as_query_engine()
        response = query_engine.query(f"Explain each {self.repo} class?")
        return response

    def explain_each_endpoint(self):
        if self.docs is None:
            self.load_data()

        index = GPTVectorStoreIndex.from_documents(self.docs)
        query_engine = index.as_query_engine()
        response = query_engine.query(f"Stipulate all endpoints with example input and output?")
        return response
