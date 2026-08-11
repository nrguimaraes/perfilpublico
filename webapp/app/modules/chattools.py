
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
from modules.arquivopt import ArquivoPT
class ChatTools:

    def __init__(self):
        self.mistral = MistralClient()
        self.arquivopt = ArquivoPT()

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

            return {"intent": "HOME_SEARCH_AUTHORS", "topic": topic, "authors": [
                author
                for author in similar
                if author["distance"] <= best + 0.1
            ]}
            
        
        elif intent == "HOME_COUNT_AUTHORS":
            topic = self.mistral.extract_topic(question)
            print(f"Topic: {topic}")
            similar = semanticSearchAuthors(topic,30)
            
            best = similar[0]["distance"]
            
            return {"intent": "HOME_COUNT_AUTHORS", "topic": topic, "count": len([
                author
                for author in similar
                if author["distance"] <= best + 0.1
            ])}

        elif intent == "HOME_TOP_TOPICS":
            return {"intent": "HOME_TOP_TOPICS", "topics": getTopTopics()}

        elif intent == "HOME_AUTHOR_TOPICS":
            author = self.mistral.extract_author(question)
            return {"intent": "HOME_AUTHOR_TOPICS", "author": author, "topics": getAuthorTopics(author)}

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
                return {"intent": "AUTHOR_TOPICS", "author": author, "topics": response}

            return {"intent": "AUTHOR_TOPICS", 
                    "author": author, 
                    "topics": topics}


        elif intent == "AUTHOR_NEWS_BY_YEAR":
            year = self.mistral.extract_year(question)
            if year is None:
                news = getAuthorAllNews(author)
                return {"intent": "AUTHOR_NEWS_BY_YEAR", 
                        "author": author, 
                        "year": None,
                        "news": news.to_dict("records")}
            
            df = getAuthorNewsByYear(author, year)
            return {"intent": "AUTHOR_NEWS_BY_YEAR", "author": author, "year": year, "news": df.to_dict("records")}

        elif intent == "AUTHOR_METADATA":
            return {"intent": "AUTHOR_METADATA", "author": author, "metadata": getAuthorMetadata(author)}

        elif intent == "AUTHOR_SEARCH_NEWS":
            topic = self.mistral.extract_topic(question)
            news = getAuthorAllNews(author)
            seen = set()
            unique_news = []

            for article in news:
                if article["Title"] not in seen:
                    seen.add(article["Title"])
                    unique_news.append(article)

            news = unique_news
            return {"intent": "AUTHOR_SEARCH_NEWS", "author": author, "topic": topic, "news": self.mistral.select_news_by_topic(topic=topic, news=news)}
        

        elif intent == "AUTHOR_TOPIC_NEWS":
            news = getAuthorNewsByTopic(author, topic)

            if news.empty:
                all_news = getAuthorAllNews(author)
                news_ = self.mistral.select_news_by_topic(topic, all_news)
            else: news_ = news.to_dict("records")

            return {"intent": "AUTHOR_TOPIC_NEWS", 
                    "topic": topic,
                    "author": author, 
                    "news": news_
            }

        elif intent == "AUTHOR_OPINION":
            topic = self.mistral.extract_topic(question)

            news = getAuthorNewsByTopic(author, topic)

            if news.empty:
                all_news = getAuthorAllNews(author)
                news_ = self.mistral.select_news_by_topic(topic, all_news)
            else: 
                news_ = news.to_dict("records")

            selected_news = news_[:5] if len(news_) > 5 else news_

            for article in selected_news:
                article["Summary"] = self.arquivopt.fetch_summary(article["Link"])


            return {
                "intent": "AUTHOR_OPINION",
                "author": author,
                "topic": topic,
                "news": selected_news
            }

        
        elif intent == "AUTHOR_TOPIC_OPINION":
            news = getAuthorNewsByTopic(author, topic)

            if news.empty:
                all_news = getAuthorAllNews(author)
                news_ = self.mistral.select_news_by_topic(topic, all_news)
            else: 
                news_ = news.to_dict("records")

            selected_news = news_[:5] if len(news_) > 5 else news_

            for article in selected_news:
                article["Summary"] = self.arquivopt.fetch_summary(article["Link"])

            return {
                "intent": "AUTHOR_TOPIC_OPINION",
                "author": author,
                "topic": topic,
                "news": selected_news
            }

        return None