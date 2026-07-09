import os
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

from pymongo import MongoClient

from framework.authorBiography.MistralClient import MistralClient

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from framework.authorBiography.ArticleFetcher import ArticleFetcher
from framework.authorBiography.BiographyChecker import BiographyChecker
from framework.authorBiography.BiographyGenerator import BiographyGenerator
from framework.authorBiography.BiographyPromptBuilder import BiographyPromptBuilder
from framework.authorBiography.MistralClient import MistralClient
from framework.authorBiography.WikipediaFetcher import WikipediaFetcher

DATABASE_NAME = "PerfilPublicoAll"
AUTHOR_NAME_FIELD = "Name"
AUTHOR_METADATA_NAME_FIELD = "name"
BIOGRAPHY_FIELD = "description"


def main() -> None:
    client = _mongo_client()
    database = client[DATABASE_NAME]

    author_collection = database.AuthorsFeaturesAll
    author_metadata_collection = database.AuthorsMetadata
    news_collection = database.NewsFeaturesAll

    generator = _build_generator(
        author_metadata_collection=author_metadata_collection,
        news_collection=news_collection,
    )

    generated_count = 0
    skipped_count = 0
    error_count = 0

    for author_name in _author_names(author_collection):
        try:
            biography = generator.generate(author_name)
        except Exception as error:
            if "RESOURCE_EXHAUSTED" in str(error):
                print("Gemini quota exceeded. Stopping generation.")
                break

            error_count += 1
            print(f"[error] {author_name}: {error}")

        biography = _normalize_biography(biography)
        if biography is None:
            skipped_count += 1
            print(f"[skip] {author_name}")
            continue

        _save_biography(author_metadata_collection, author_name, biography)
        generated_count += 1
        print(f"[generated] {author_name}")

    print(
        "Finished biography generation: "
        f"{generated_count} generated, "
        f"{skipped_count} skipped, "
        f"{error_count} errors."
    )


def _mongo_client() -> MongoClient:
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        return MongoClient(mongo_uri)

    return MongoClient(host="localhost", port=27017)


def _build_generator(
    author_metadata_collection: Any,
    news_collection: Any,
) -> BiographyGenerator:
    return BiographyGenerator(
        biography_checker=BiographyChecker(author_metadata_collection),
        article_fetcher=ArticleFetcher(news_collection),
        wikipedia_fetcher=WikipediaFetcher(),
        prompt_builder=BiographyPromptBuilder(),
        mistral_client=MistralClient(),
    )


def _author_names(author_collection: Any) -> Iterable[str]:
    authors = author_collection.find({}, {AUTHOR_NAME_FIELD: 1, "_id": 0})

    for author in authors:
        author_name = _normalize_author_name(author.get(AUTHOR_NAME_FIELD))
        if author_name is not None:
            yield author_name


def _normalize_author_name(author_name: Any) -> Optional[str]:
    if not isinstance(author_name, str):
        return None

    author_name = author_name.strip()
    if not author_name:
        return None

    return author_name


def _normalize_biography(biography: Any) -> Optional[str]:
    if not isinstance(biography, str):
        return None

    biography = biography.strip()
    if not biography:
        return None

    return biography


def _save_biography(
    author_metadata_collection: Any,
    author_name: str,
    biography: str,
) -> None:
    author_metadata_collection.update_one(
        {AUTHOR_METADATA_NAME_FIELD: author_name},
        {
            "$set": {BIOGRAPHY_FIELD: biography},
            "$setOnInsert": {AUTHOR_METADATA_NAME_FIELD: author_name},
        },
        upsert=True,
    )


if __name__ == "__main__":
    main()
