from typing import Any, Iterable, Mapping, Optional

ArticleData = dict[str, Optional[str]]

ARTICLE_FIELD_CANDIDATES: Mapping[str, tuple[str, ...]] = {
    "title": ("Title", "title"),
    "section": ("Topic", "Section", "section", "Topics"),
}


class ArticleFetcher:

    def __init__(
        self,
        news_features_collection: Any,
    ) -> None:
        if news_features_collection is None:
            raise ValueError("news_features_collection is required")

        if not hasattr(news_features_collection, "find"):
            raise ValueError("news_features_collection must provide find")

        self.news_features_collection = news_features_collection


    def fetch(self, author_name: str, limit:Optional[int]=None) -> list[ArticleData]:
        cursor = (
            self.news_features_collection
            .find({"Author_clean": author_name}, self._projection())
            .sort("ExtractionDate", -1)
        )
        articles = []
        seen_titles = set()

        for document in cursor:
            article = self._extract_article(document)

            title = article["title"]
            if title in seen_titles:
                continue

            seen_titles.add(title)
            articles.append(article)
            if limit is not None and len(articles) >= limit:
                break

        return articles


    @staticmethod
    def _projection() -> Mapping[str, int]:
        projection = {"_id": 0}
        for source_fields in ARTICLE_FIELD_CANDIDATES.values():
            for source_field in source_fields:
                projection[source_field] = 1

        return projection


    def _extract_article(self, document: Mapping[str, Any]) -> ArticleData:
        return {
            field: self._extract_first_text(document, source_fields)
            for field, source_fields in ARTICLE_FIELD_CANDIDATES.items()
        }


    @staticmethod
    def _extract_first_text(
        document: Mapping[str, Any],
        source_fields: tuple[str, ...],
    ) -> Optional[str]:
        for source_field in source_fields:
            text = ArticleFetcher._extract_text(document.get(source_field))
            if text is not None:
                return text

        return None


    @staticmethod
    def _extract_text(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None

        text = value.strip()
        if not text:
            return None

        return text
