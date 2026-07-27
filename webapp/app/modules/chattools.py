from pydoc_data.topics import topics

from modules.mongointerface import (
    semanticSearchAuthors,
    getAuthorNewsCount,
    getAuthorNewsByYear,
    getAuthorMetadata,
    getAuthorTopicNewsCount,
    getAuthorNewsByTopic,
    getTopTopics,
    getAuthorTopics,
    getAuthorAllNews,
)

from modules.mistralclient import MistralClient

class ChatTools:

    def __init__(self):
        self.mistral = MistralClient()

    def execute(
        self,
        intent,
        question,
        author=None,
        topic=None,
    ):

        if intent == "HOME_SEARCH_AUTHORS":
            topic = self.mistral.extract_topic(question)
            similar = semanticSearchAuthors(topic,30)
            
            best = similar[0]["distance"]

            return [
                author
                for author in similar
                if author["distance"] <= best + 0.1
            ]
            
        
        elif intent == "HOME_COUNT_AUTHORS":
            topic = self.mistral.extract_topic(question)
            print(f"Topic: {topic}")
            similar = semanticSearchAuthors(topic,30)
            
            best = similar[0]["distance"]
            
            return len([
                author
                for author in similar
                if author["distance"] <= best + 0.1
            ])

        elif intent == "HOME_TOP_TOPICS":
            return getTopTopics()

        elif intent == "HOME_AUTHOR_TOPICS":
            author = self.mistral.extract_author(question)
            return getAuthorTopics(author)

        elif intent == "AUTHOR_TOPICS":
            topics = getAuthorTopics(author)

            if not topics:
                metadata = getAuthorMetadata(author)
                prompt = f"""
                    Estes são os dados de um jornalista.
                    Biografia:
                    {metadata["description"]}
                    Enumera apenas os seis principais temas abordados por este jornalista.
                    Responde apenas com uma lista separada por vírgulas.
                """
                response = self.mistral.chat(prompt)
                return response

            return topics


        elif intent == "AUTHOR_NEWS_BY_YEAR":
            year = self.mistral.extract_year(question)
            df = getAuthorNewsByYear(author, year)
            return df.to_dict("records")
        
        elif intent == "AUTHOR_METADATA":
            return getAuthorMetadata(author)
        
        elif intent == "AUTHOR_SEARCH_NEWS":
            topic = self.mistral.extract_topic(question)
            print(topic)
            news = getAuthorAllNews(author)
            seen = set()
            unique_news = []

            for article in news:
                if article["Title"] not in seen:
                    seen.add(article["Title"])
                    unique_news.append(article)

            news = unique_news
            return self.mistral.select_news_by_topic(topic=topic, news=news)
        

        elif intent == "AUTHOR_TOPIC_NEWS":
            news = getAuthorNewsByTopic(author, topic)

            if news.empty:
                all_news = getAuthorAllNews(author)
                return self.mistral.select_news_by_topic(topic, all_news)

            return news.to_dict("records")

        return None