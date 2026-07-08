from dataclasses import dataclass
from typing import Any, Mapping, Optional

@dataclass(frozen=True)
class BiographyStatus:
    author_name: str
    has_biography: bool
    biography: Optional[str] = None


class BiographyChecker:

    def __init__(
        self,
        author_metadata_collection: Any,
        biography_field: str = "description",
    ) -> None:
        self.author_metadata_collection = author_metadata_collection
        self.biography_field = biography_field


    def check(self, author_name: str) -> BiographyStatus:
        normalized_author_name = self._normalize_author_name(author_name)
        document = self.author_metadata_collection.find_one(
            {"name": normalized_author_name},
            {"name": 1, self.biography_field: 1},
        )
        biography = self._extract_biography(document)

        return BiographyStatus(
            author_name=normalized_author_name,
            has_biography=biography is not None,
            biography=biography,
        )


    def has_biography(self, author_name: str) -> bool:
        return self.check(author_name).has_biography


    def get_existing_biography(self, author_name: str) -> Optional[str]:
        return self.check(author_name).biography


    @staticmethod
    def _normalize_author_name(author_name: str) -> str:
        if author_name is None:
            raise ValueError("author_name is required")

        normalized_author_name = author_name.strip()
        if not normalized_author_name:
            raise ValueError("author_name cannot be empty")

        return normalized_author_name


    def _extract_biography(
        self,
        document: Optional[Mapping[str, Any]],
    ) -> Optional[str]:
        if not document:
            return None

        biography = document.get(self.biography_field)
        if not isinstance(biography, str):
            return None

        biography = biography.strip()
        if not biography:
            return None

        return biography
