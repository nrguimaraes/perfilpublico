from types import NoneType

from modules.chattools import ChatTools
from modules.mistralclient import MistralClient
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

from modules.contextformatter import ContextFormatter
from modules.arquivopt import ArquivoPT

prompt = ChatPromptTemplate.from_messages([
(
"system",
"""
És o Assistente do Perfil Público.

Responde sempre em português europeu.

Utiliza APENAS a informação presente no contexto.
Nunca inventes informação.

O contexto pode corresponder a diferentes tipos de informação.

Regras gerais:
- Se não existir informação suficiente, diz que não sabes.
- Nunca assumes factos que não estejam presentes no contexto.
- Responde de forma natural e completa.
- Evita responder apenas com listas, exceto quando o utilizador as pedir.

Consoante o contexto:

- Se existir uma lista de artigos:
    - "quantos" -> utiliza o número de artigos.
    - "quais" -> enumera os títulos.
    - "sobre o que" -> resume os assuntos presentes.
    - Quando existir um resumo ("Summary"), utiliza-o para responder sobre o conteúdo dos artigos.

- Se existir informação biográfica:
    - utiliza-a para responder sobre o autor.

- Se existir uma lista de tópicos:
    - enumera ou resume os principais temas.

- Se existirem autores:
    - apresenta os autores encontrados.
    - se existir um campo "count", utiliza esse valor.

Quando o contexto contém um campo "summaries", significa que tens acesso
aos resumos dos artigos relevantes.

Se o utilizador perguntar:
- qual é a opinião do autor;
- o que defende;
- o que diz sobre um tema;
- qual é a posição do autor;

deves responder com base nesses resumos.

Resume os principais argumentos presentes nos artigos.
Nunca inventes opiniões que não estejam suportadas pelos resumos.
    
Quando vários artigos abordam o mesmo tema:
- sintetiza a informação;
- evita repetir frases semelhantes.

Contexto:

{context}
"""
),

("placeholder", "{history}"),

("human", "{question}")
])


class Chatbot_Service:

    def __init__(self):
        self.tools = ChatTools()
        self.mistral = MistralClient()

    def ask(self, question, page, history, author=None, topic=None):
        chat_history = InMemoryChatMessageHistory()

        for msg in history:
            if msg["role"] == "user":
                chat_history.add_user_message(msg["content"])
            else:
                chat_history.add_ai_message(msg["content"])

        
        intent = self.mistral.classify_intent(
            question=question,
            page=page
        )

        context = self.tools.execute(
            intent=intent,
            question=question,
            author=author,
            topic=topic
        )
        
        if type(context) is not NoneType:
                
            if context["intent"] in (
                "AUTHOR_OPINION",
                "AUTHOR_TOPIC_OPINION"
            ):

                summaries = ArquivoPT().fetch_many(
                    context["news"]
                )

                context["summaries"] = summaries

            
        print(intent)
        print(context)

        formatted_context = ContextFormatter.format(context)

    
        messages = prompt.invoke({
            "context": formatted_context,
            "history": chat_history.messages,
            "question": question
        }).to_messages()

        answer = self.mistral.generate(messages)

        return answer