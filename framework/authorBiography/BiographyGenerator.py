from typing import Optional

from framework.authorBiography.ArticleFetcher import ArticleFetcher
from framework.authorBiography.BiographyChecker import BiographyChecker
from framework.authorBiography.BiographyPromptBuilder import BiographyPromptBuilder
from framework.authorBiography.MistralClient import MistralClient
from framework.authorBiography.WikipediaFetcher import WikipediaFetcher

MAX_ARTICLES_WITH_WIKIPEDIA = 20
MAX_ARTICLES_WITHOUT_WIKIPEDIA = 40


class BiographyGenerator:

    def __init__(
        self,
        biography_checker: BiographyChecker,
        article_fetcher: ArticleFetcher,
        wikipedia_fetcher: WikipediaFetcher,
        prompt_builder: BiographyPromptBuilder,
        mistral_client: MistralClient,
    ) -> None:
        self.biography_checker = biography_checker
        self.article_fetcher = article_fetcher
        self.wikipedia_fetcher = wikipedia_fetcher
        self.prompt_builder = prompt_builder
        self.mistral_client = mistral_client


    def generate(self, author_name: str) -> Optional[str]:
        if not self.biography_checker.needs_generation(author_name):
            return None

        wikipedia_information = self.wikipedia_fetcher.fetch(author_name)

        if wikipedia_information:
            limit = MAX_ARTICLES_WITH_WIKIPEDIA
        else:
            limit = MAX_ARTICLES_WITHOUT_WIKIPEDIA

        articles = self.article_fetcher.fetch(
            author_name,
            limit=limit,
        )

        prompt = self.prompt_builder.build(
            author_name=author_name,
            wikipedia_information=wikipedia_information,
            articles=articles,
        )

        biography = self.mistral_client.generate(prompt)

        return biography