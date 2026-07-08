from typing import Any, Mapping, Optional
from urllib.parse import quote

import requests

TIMEOUT = 10
WIKIDATA = {
    "P106": ("ocupação", "entity"),
    "P27": ("nacionalidade", "entity"),
    "P108": ("empregador", "entity"),
    "P69": ("educação", "entity"),
    "P166" : ("distinções", "entity"),
    "P569": ("nascimento", "date")
}

class WikipediaFetcher:

    def __init__(
        self,
        session: Optional[Any] = None,
        timeout: int = TIMEOUT,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.user_agent = "PerfilPublico"
        self.base_url = f"https://pt.wikipedia.org"
        self.wikidata_api_url = "https://www.wikidata.org/w/api.php"
        self.wikidata_entity_url = "https://www.wikidata.org/wiki/Special:EntityData"


    def fetch(self, author_name: str) -> Optional[Mapping[str, Any]]:
        normalized_author_name = self._normalize_author_name(author_name)
        page_key = self._find_page_key(normalized_author_name)
        if page_key is None:
            return None

        page_data = self._fetch_page_data(page_key)
        if page_data is None:
            return None

        summary = self._extract_summary(page_data)
        if summary is None:
            return None

        wikidata_id = self._extract_wikidata_id(page_data)
        wikidata = self._fetch_wikidata_biography(wikidata_id)
        return {
            "sumário": summary,
            **wikidata,
        }


    @staticmethod
    def _normalize_author_name(author_name: str) -> str:
        if author_name is None:
            raise ValueError("author_name is required")

        normalized_author_name = author_name.strip()
        if not normalized_author_name:
            raise ValueError("author_name cannot be empty")

        return normalized_author_name


    def _find_page_key(self, author_name: str) -> Optional[str]:
        data = self._get_json(
            f"{self.base_url}/w/rest.php/v1/search/page",
            params={"q": author_name, "limit": 5},
        )

        if data is None:
            return None

        pages = data.get("pages")
        if not isinstance(pages, list) or not pages:
            return None

        for page in pages:
            if self._matches_author_name(author_name, page):
                return self._extract_page_key(page)
        return None

    def _fetch_page_data(self, page_key: str) -> Optional[Mapping[str, Any]]:
        encoded_page_key = quote(page_key, safe="")
        data = self._get_json(
            f"{self.base_url}/api/rest_v1/page/summary/{encoded_page_key}"
        )

        return data

    @staticmethod
    def _extract_wikidata_id(page_data: Mapping[str, Any]) -> Optional[str]:
        wikidata_id = page_data.get("wikibase_item")
        if not isinstance(wikidata_id, str):
            return None

        wikidata_id = wikidata_id.strip()
        if not wikidata_id:
            return None

        return wikidata_id


    def _fetch_wikidata(self, wikidata_id: str) -> Optional[Mapping[str, Any]]:
        return self._get_json(
            f"{self.wikidata_entity_url}/{wikidata_id}.json"
        )


    def _fetch_wikidata_biography(
        self,
        wikidata_id: Optional[str],
    ) -> Mapping[str, Any]:
        biography = self._empty_wikidata_biography()
        if wikidata_id is None:
            return biography

        data = self._fetch_wikidata(wikidata_id)
        entity = self._extract_wikidata_entity(data, wikidata_id)
        if entity is None:
            return biography

        claims = self._extract_claims(entity)
        entity_values = self._extract_entity_claims(claims)
        qids = self._collect_qids(entity_values)
        labels = self._resolve_wikidata_labels(qids)

        for property_id, (name, tipo) in WIKIDATA.items():
            if tipo == "entity":
                biography[name] = self._labels_for_qids(
                    entity_values.get(property_id, []),
                    labels,
                )

            else:
                biography[name] = self._extract_date_claim(claims, property_id)

        return biography


    @staticmethod
    def _empty_wikidata_biography() -> dict[str, Any]:
        biography = {}

        for _, (name, tipo) in WIKIDATA.items():
            biography[name] = [] if tipo == "entity" else None

        return biography


    @staticmethod
    def _extract_wikidata_entity(
        data: Optional[Mapping[str, Any]],
        wikidata_id: str,
    ) -> Optional[Mapping[str, Any]]:
        if data is None:
            return None

        entities = data.get("entities")
        if not isinstance(entities, Mapping):
            return None

        entity = entities.get(wikidata_id)
        if not isinstance(entity, Mapping):
            return None

        return entity


    @staticmethod
    def _extract_claims(entity: Mapping[str, Any]) -> Mapping[str, Any]:
        claims = entity.get("claims")
        if not isinstance(claims, Mapping):
            return {}

        return claims


    def _extract_entity_claims(
        self,
        claims: Mapping[str, Any],
    ) -> Mapping[str, list[str]]:
        return {
            property_id: self._extract_entity_claim_qids(claims, property_id)
            for property_id, (_, tipo) in WIKIDATA.items()
            if tipo == "entity"
        }


    def _extract_entity_claim_qids(
        self,
        claims: Mapping[str, Any],
        property_id: str,
    ) -> list[str]:
        values = claims.get(property_id)
        if not isinstance(values, list):
            return []

        qids = []
        for claim in values:
            qid = self._extract_entity_claim_qid(claim)
            if qid is not None and qid not in qids:
                qids.append(qid)

        return qids


    @staticmethod
    def _extract_entity_claim_qid(claim: Any) -> Optional[str]:
        if not isinstance(claim, Mapping):
            return None

        mainsnak = claim.get("mainsnak")
        if not isinstance(mainsnak, Mapping):
            return None

        datavalue = mainsnak.get("datavalue")
        if not isinstance(datavalue, Mapping):
            return None

        value = datavalue.get("value")
        if not isinstance(value, Mapping):
            return None

        qid = value.get("id")
        if not isinstance(qid, str):
            numeric_id = value.get("numeric-id")
            if not isinstance(numeric_id, int):
                return None

            qid = f"Q{numeric_id}"

        qid = qid.strip()
        if not qid:
            return None

        return qid


    @staticmethod
    def _extract_date_claim(
        claims: Mapping[str, Any],
        property_id: str,
    ) -> Optional[str]:
        values = claims.get(property_id)
        if not isinstance(values, list):
            return None

        for claim in values:
            date = WikipediaFetcher._extract_date_claim_value(claim)
            if date is not None:
                return date

        return None


    @staticmethod
    def _extract_date_claim_value(claim: Any) -> Optional[str]:
        if not isinstance(claim, Mapping):
            return None

        mainsnak = claim.get("mainsnak")
        if not isinstance(mainsnak, Mapping):
            return None

        datavalue = mainsnak.get("datavalue")
        if not isinstance(datavalue, Mapping):
            return None

        value = datavalue.get("value")
        if not isinstance(value, Mapping):
            return None

        date = value.get("time")
        if not isinstance(date, str):
            return None

        date = date.strip()
        if not date:
            return None

        return date.lstrip("+").split("T", 1)[0]


    @staticmethod
    def _collect_qids(entity_values: Mapping[str, list[str]]) -> list[str]:
        qids = []
        for property_qids in entity_values.values():
            for qid in property_qids:
                if qid not in qids:
                    qids.append(qid)

        return qids


    def _resolve_wikidata_labels(self, qids: list[str]) -> Mapping[str, str]:
        if not qids:
            return {}

        data = self._get_json(
            self.wikidata_api_url,
            params={
                "action": "wbgetentities",
                "ids": "|".join(qids),
                "props": "labels",
                "languages": "pt|en|es|de|fr",
                "format": "json",
            },
        )
        if data is None:
            return {}

        return self._extract_wikidata_labels(data)


    @staticmethod
    def _extract_wikidata_labels(data: Mapping[str, Any]) -> Mapping[str, str]:
        entities = data.get("entities")
        if not isinstance(entities, Mapping):
            return {}

        labels = {}
        for qid, entity in entities.items():
            if not isinstance(qid, str) or not isinstance(entity, Mapping):
                continue

            entity_labels = entity.get("labels")
            if not isinstance(entity_labels, Mapping):
                continue
            langs=  ["pt", "en", "es", "de", "fr"]
            for lang in langs:
                label_data = entity_labels.get(lang)
                if not isinstance(label_data, Mapping):
                    continue

                label = label_data.get("value")
                if not isinstance(label, str):
                    continue

                label = label.strip()
                if label:
                    labels[qid] = label
                    break
        return labels


    @staticmethod
    def _labels_for_qids(
        qids: list[str],
        labels: Mapping[str, str],
    ) -> list[str]:
        values = []
        for qid in qids:
            label = labels.get(qid)
            if label is not None and label not in values:
                values.append(label)

        return values


    def _get_json(
        self,
        url: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        try:
            response = self.session.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException:
            return None

        if getattr(response, "status_code", None) != 200:
            return None

        try:
            data = response.json()
        except (AttributeError, ValueError):
            return None

        if not isinstance(data, Mapping):
            return None

        return data


    def _headers(self) -> Mapping[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }


    @staticmethod
    def _extract_page_key(page: Mapping[str, Any]) -> Optional[str]:
        page_key = page.get("key") or page.get("title")
        if not isinstance(page_key, str):
            return None

        page_key = page_key.strip()
        if not page_key:
            return None

        return page_key


    @staticmethod
    def _extract_summary(page_summary: Mapping[str, Any]) -> Optional[str]:
        summary = page_summary.get("extract") or page_summary.get("description")
        if not isinstance(summary, str):
            return None

        summary = summary.strip()
        if not summary:
            return None

        return summary

    @staticmethod
    def _matches_author_name(author_name: str, page: Mapping[str, Any]) -> bool:
        title = page.get("title", "").casefold().strip()
        author = author_name.casefold().strip()

        return (
            title == author
            or title.startswith(author + " (")
        )
