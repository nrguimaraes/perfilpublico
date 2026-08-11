class ContextFormatter:

    @staticmethod
    def format(context):

        if context is None:
            return "Sem contexto."

        intent = context["intent"]

        if intent == "HOME_SEARCH_AUTHORS":

            text = f"Tópico: {context['topic']}\n\nAutores encontrados:\n"

            for author in context["authors"]:
                text += f"- {author['Name']}\n"

            return text


        elif intent == "HOME_COUNT_AUTHORS":

            return (
                f"Tópico: {context['topic']}\n"
                f"Foram encontrados {context['count']} autores."
            )


        elif intent == "AUTHOR_METADATA":

            metadata = context["metadata"]

            return f"""
                Autor: {context['author']}

                Cargo:
                {metadata["author_role"]}

                Jornal:
                {metadata["newspaper"]}

                Biografia:
                {metadata["description"]}
                """

        elif intent == "AUTHOR_TOPIC_NEWS":

            txt = f"Autor: {context['author']}\n"
            txt += f"Tópico: {context['topic']}\n\n"
            txt += "Artigos:\n"

            for article in context["news"]:

                txt += (
                    f"- {article['Title']} "
                    f"({article['ExtractionDate']})\n"
                )

            return txt

        elif intent == "AUTHOR_OPINION" or intent == "AUTHOR_TOPIC_OPINION":

            text = f"Autor: {context['author']}\n"
            text += f"Tópico: {context['topic']}\n\n"

            text += "Artigos:\n"

            for article in context["summaries"]:

                text += f"""
                    Título:
                    {article['title']}

                    Resumo:
                    {article['summary']}

                    """
                    
        return str(context)