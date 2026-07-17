import os

from pymongo import MongoClient

from framework.authorBiography.ArticleFetcher import ArticleFetcher
from framework.authorBiography.MistralClient import MistralClient
from framework.recommendationFeatures.AuthorSummarization import AuthorSummarization
from framework.recommendationFeatures.BuildEmeddings import BuildEmbeddings
from framework.recommendationFeatures.ChromaRep import ChromaRep


client = MongoClient(os.getenv("MONGO_URI"))
db = client.PerfilPublicoAll


def main():

    builder = BuildEmbeddings(
        author_collection=db.AuthorsFeaturesAll,
        article_fetcher=ArticleFetcher(db.NewsFeaturesAll),
        summarizer=AuthorSummarization(),
        mistral=MistralClient(),
        repository=ChromaRep(),
    )

    builder.build()


if __name__ == "__main__":
    main()