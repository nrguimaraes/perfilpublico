import json
import os
from mistralai.client import Mistral




class MistralClient:

    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    def embed(self, text: str):
        response = self.client.embeddings.create(
            model="mistral-embed",
            inputs=[text],
        )

        return response.data[0].embedding
    

    def classify_intent(self, question: str, page: str):
    
        prompt = f"""
            És um classificador de intenções para um chatbot de um portal de notícias.

            A tua única tarefa é decidir qual a operação que o backend deve executar.

            Não respondas à pergunta.
            Responde apenas com UMA das intenções abaixo.

            Página atual:
            {page}

            Não escolhas intenções de outras páginas.
            Escolhe apenas uma intenção válida para essa página.

            Home:
            - HOME_SEARCH_AUTHORS: encontrar autores relacionados com um tema, na pagina home.
            - HOME_COUNT_AUTHORS: contar autores relacionados com um tema, na pagina home.
            - HOME_TOP_TOPICS: obter os tópicos mais populares, na pagina home.
            - HOME_AUTHOR_TOPICS: obter os tópicos de um autor, na pagina home.

            Author:
                Esta página representa um autor específico
                O autor já é conhecido pelo sistema.

            - AUTHOR_TOPICS: obter os tópicos de um autor, na pagina author.
            - AUTHOR_NEWS_BY_YEAR: listar artigos de um determinado ano, na pagina author.
            - AUTHOR_METADATA: obter informações metadata de um autor, na pagina author.
            - AUTHOR_SEARCH_NEWS: encontrar artigos de um autor relacionados com um tema ou palavra-chave, na pagina author.
            
            Author_Topic: 
                Esta página representa um autor e um tópico específico
                O autor e tópico já são conhecidos pelo sistema.

            - AUTHOR_TOPIC_NEWS: listar artigos de um tópico de um autor, na pagina author_topic.

            Se nenhuma intenção corresponder, responde:
            UNKNOWN

            Pergunta:
            {question}
        """

        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()
    

    def extract_topic(self, question: str):
        prompt = f"""
            O teu objetivo é extrair apenas o tema principal da pergunta.

            Regras:
            - Responde apenas com o tema.
            - Não escrevas frases.
            - Não expliques.
            - Mantém o tema na mesma língua da pergunta.
            - Não utilizes abreviações ou siglas.
            exemplo:
                "ia": topico= "inteligência artificial",
                "ai": topico= "inteligência artificial",
                "ue": topico= "união europeia",
                "eua": topico= "estados unidos",
                "usa": topico= "estados unidos",
                "covid": topico= "covid-19",
            - Se não existir um tema, responde apenas:
            NONE

            Exemplos:

            Pergunta:
            Que autores escrevem sobre inteligência artificial?
            Resposta:
            inteligência artificial
            
            Pergunta:
            Que autores escrevem sobre IA?
            Resposta:
            inteligência artificial

            Pergunta:
            Quem fala de alterações climáticas?
            Resposta:
            alterações climáticas

            Pergunta:
            Há jornalistas que escrevam sobre o PSD?
            Resposta:
            PSD

            Pergunta:
            Quais os tópicos mais populares?
            Resposta:
            NONE

            Pergunta:
            {question}
            
        """
        
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()
    
    def extract_author(self, question: str):
        prompt = f"""
            O teu objetivo é extrair apenas o nome do autor da pergunta.

            Regras:
            - Responde apenas com o nome do autor.
            - Não escrevas frases.
            - Não expliques.
            - Mantém o nome do autor na mesma língua da pergunta.
            - Se não existir um autor, responde apenas:
            NONE

            Exemplos:

            Pergunta:
            Que autores escrevem sobre inteligência artificial?
            Resposta:
            NONE

            Pergunta:
            Camilo Soldado escreve sobre o ambiente?
            Resposta:
            Camilo Soldado

            Pergunta:
            António Costa é um dos temas de Ascenso Simões?
            Resposta:
            Ascenso Simões

            Pergunta:
            {question}
            
        """
        
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()

    def extract_topic(self, question: str):
        prompt = f"""
            O teu objetivo é extrair apenas o tema principal da pergunta.

            Regras:
            - Responde apenas com o tema.
            - Não escrevas frases.
            - Não expliques.
            - Mantém o tema na mesma língua da pergunta.
            - Se não existir um tema, responde apenas:
            NONE

            Exemplos:

            Pergunta:
            Que autores escrevem sobre inteligência artificial?
            Resposta:
            inteligência artificial

            Pergunta:
            Quem fala de alterações climáticas?
            Resposta:
            alterações climáticas

            Pergunta:
            Há jornalistas que escrevam sobre o PSD?
            Resposta:
            PSD

            Pergunta:
            Quais os tópicos mais populares?
            Resposta:
            NONE

            Pergunta:
            {question}
            
        """
        
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()


    def extract_year(self, question: str):
        prompt = f"""
            O teu objetivo é extrair apenas o ano a que a pergunta se refere.

            Regras:
            - Responde apenas com o ano.
            - Não escrevas frases.
            - Não expliques.
            - Se não existir um ano, responde apenas:
            NONE

            Exemplos:

            Pergunta:
            Quantos artigos o autor escreveu em 2020?
            Resposta:
            2020

            Pergunta:
            Sobre que temas ele falou em dois mil e dezassete?
            Resposta:
            2017

            Pergunta:
            Ele escrevesobre o PSD?
            Resposta:
            NONE

            Pergunta:
            {question}
            
        """
        
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()
    
    def chat(self, prompt: str):
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()  
    
    def select_news_by_topic(self, topic: str, news: list):
        prompt = f"""
            Vais receber um tema e uma lista de títulos de artigos.

            Seleciona apenas os artigos cujo título menciona explicitamente o tema
            ou um sinónimo muito próximo.

            Não assumas o conteúdo do artigo.
            Não infiras relações indiretas.
            Não escolhas artigos apenas porque pertencem à mesma área.

            Se o título não indicar claramente que o artigo é sobre esse tema, não o seleciones.
            Se nenhum título mencionar claramente o tema, responde:
            NONE

            Responde apenas com um array JSON.

            Exemplo:
            [1,3]

            Se não existir nenhum:
            NONE

            Tema procurado:
            "{topic}"

            Notícias:
        """

        
        for i, article in enumerate(news):
            prompt += f"\n{i}. {article['Title']}"

        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()


        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()
        
        if content == "NONE":
            return []
        
        indices = json.loads(content)

        return [news[i] for i in indices]