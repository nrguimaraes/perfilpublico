from typing import Any, Iterable, Mapping, Optional

ARTICLE_LABELS: tuple[tuple[str, str], ...] = (
    ("title", "Título"),
    ("section", "Secção"),
)


class BiographyPromptBuilder:

    def build(
        self,
        author_name: str,
        wikipedia_information: Optional[Mapping[str, Any]],
        articles: Iterable[Mapping[str, Any]],
    ) -> str:
        normalized_author_name = self._normalize_author_name(author_name)
        normalized_articles = self._normalize_articles(articles)

        return "\n\n".join(
            [
                self._instructions(),
                f"Nome do jornalista: {normalized_author_name}",
                self._format_wikipedia_information(wikipedia_information),
                self._format_articles(normalized_articles),
            ]
        )


    @staticmethod
    def _normalize_author_name(author_name: str) -> str:
        if author_name is None:
            raise ValueError("author_name is required")

        normalized_author_name = author_name.strip()
        if not normalized_author_name:
            raise ValueError("author_name cannot be empty")

        return normalized_author_name


    @staticmethod
    def _normalize_articles(
        articles: Iterable[Mapping[str, Any]],
    ) -> list[Mapping[str, Any]]:
        if articles is None:
            raise ValueError("articles is required")

        return [
            article
            for article in articles
            if isinstance(article, Mapping)
        ]


    @staticmethod
    def _instructions() -> str:
        return (
            "Objetivo: escrever uma biografia profissional em português de Portugal com"
            " no mínimo 65 palavras e no máximo 100 palavras,"
            " factual, neutra e concisa sobre o jornalista indicado."
            "Usa a informação da Wikipédia apenas como contexto e usa os"
            " artigos para perceber áreas de especialização, percurso editorial e"
            " temas recorrentes da carreira. Nunca inventes informação nem incluas"
            " dados que não estejam suportados pela informação fornecida. Se a informação "
            "da Wikipédia parecer referir-se a outra pessoa com o mesmo nome ou for "
            "incompatível com o perfil inferido a partir dos artigos, ignora-a "
            "completamente e baseia-te apenas nos artigos. A resposta final deve "
            "conter apenas texto corrido, sem tópicos, bullets, listas, títulos ou metacomentários." 
            "Nunca atribuas profissões, cargos, afiliações ou qualificações que não estejam "
            "explicitamente presentes na informação fornecida. Se apenas for possível concluir"
            " que escreve artigos de opinião ou notícias, limita-te a descrevê-lo como jornalista"
            " ou autor de artigos, sem inferir outras funções que não estejam explicitamente indicadas."
            "Privilegia uma descrição baseada na atividade jornalística observável. "
            "Em vez de inferir cargos, notoriedade ou características pessoais, "
            "descreve os principais temas abordados, áreas de interesse, "
            "percurso editorial e tipo de conteúdos publicados. Quando "
            "a informação disponível for limitada, produz uma biografia sóbria "
            "e factual, centrada na produção jornalística, evitando linguagem"
            " elogiosa ou especulativa."
        )


    def _format_wikipedia_information(
        self,
        wikipedia_information: Optional[Mapping[str, Any]],
    ) -> str:
        if not wikipedia_information:
            return "Informação da Wikipédia: não disponível."

        lines = ["Informação da Wikipédia:"]
        for key, value in wikipedia_information.items():
            formatted_value = self._format_value(value)
            if formatted_value is None:
                continue

            lines.append(f"{key}: {formatted_value}")

        if len(lines) == 1:
            lines.append("não disponível")

        return "\n".join(lines)


    def _format_articles(self, articles: list[Mapping[str, Any]]) -> str:
        if not articles:
            return "Artigos do jornalista: não disponíveis."

        article_blocks = [
            self._format_article(article, index)
            for index, article in enumerate(articles, start=1)
        ]

        return "Artigos do jornalista:\n" + "\n\n".join(article_blocks)


    def _format_article(
        self,
        article: Mapping[str, Any],
        index: int,
    ) -> str:
        lines = [f"Artigo {index}:"]

        for field, label in ARTICLE_LABELS:
            formatted_value = self._format_value(article.get(field))
            if formatted_value is None:
                continue

            lines.append(f"{label}: {formatted_value}")

        return "\n".join(lines)


    def _format_value(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, str):
            return self._format_text(value)

        if isinstance(value, Mapping):
            return self._format_mapping(value)

        if isinstance(value, (list, tuple, set)):
            return self._format_iterable(value)

        return self._format_text(str(value))


    @staticmethod
    def _format_text(value: str) -> Optional[str]:
        text = value.strip()
        if not text:
            return None

        return text


    def _format_iterable(self, values: Iterable[Any]) -> Optional[str]:
        formatted_values = []
        for value in values:
            formatted_value = self._format_value(value)
            if formatted_value is not None:
                formatted_values.append(formatted_value)

        if not formatted_values:
            return None

        return ", ".join(formatted_values)


    def _format_mapping(self, value: Mapping[str, Any]) -> Optional[str]:
        formatted_items = []
        for item_key, item_value in value.items():
            formatted_value = self._format_value(item_value)
            if formatted_value is None:
                continue

            formatted_items.append(f"{item_key}: {formatted_value}")

        if not formatted_items:
            return None

        return "; ".join(formatted_items)
